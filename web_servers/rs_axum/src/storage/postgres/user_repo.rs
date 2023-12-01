use crate::usecases::base_entities::AccessModelError;
use crate::usecases::users::entities::{User, UserForUpdate};
use crate::usecases::users::get_user::FindUserById;
use crate::usecases::users::user_updater::UpdateUser;
use async_trait::async_trait;
use deadpool_postgres::{Pool, PoolError};
use log::error;
use tokio_postgres::Row;

impl From<PoolError> for AccessModelError {
    fn from(err: PoolError) -> AccessModelError {
        error!("Pool error: {}", err);
        AccessModelError::FatalError
    }
}

impl From<tokio_postgres::Error> for AccessModelError {
    fn from(err: tokio_postgres::Error) -> AccessModelError {
        error!("General db error: {}", err);
        AccessModelError::FatalError
    }
}

pub struct UserRepo<'a> {
    db_pool: &'a Pool,
}

impl UserRepo<'_> {
    pub fn new<'a>(db_pool: &'a Pool) -> UserRepo {
        UserRepo { db_pool }
    }
}

const GET_BY_ID_QUERY: &str = r#"
    SELECT
        user_id,
        username,
        email,
        is_archived,
        created_at
    FROM users
    WHERE user_id=$1
"#;

const UPDATE_USER_QUERY: &str = r#"
    UPDATE users
    SET
        username=$2,
        email=$3,
        updated_at=NOW()
    WHERE user_id=$1
    RETURNING
        user_id,
        username,
        email,
        is_archived,
        created_at
"#;

impl TryFrom<Row> for User {
    type Error = AccessModelError;

    fn try_from(row: Row) -> Result<User, Self::Error> {
        Ok(User::new(
            row.try_get("user_id")?,
            row.try_get("username")?,
            row.try_get("email")?,
            row.try_get("is_archived")?,
            row.try_get("created_at")?,
        ))
    }
}

#[async_trait]
impl FindUserById for UserRepo<'_> {
    async fn find_user_by_id(&self, user_id: i32) -> Result<User, AccessModelError> {
        let client = self.db_pool.get().await?;

        match client.query_opt(GET_BY_ID_QUERY, &[&user_id]).await? {
            Some(row) => Ok(row.try_into()?),
            None => Err(AccessModelError::NotFoundError),
        }
    }
}

#[async_trait]
impl UpdateUser for UserRepo<'_> {
    async fn update_user_in_storage(&self, user: UserForUpdate) -> Result<User, AccessModelError> {
        let client = self.db_pool.get().await?;

        match client
            .query_opt(
                UPDATE_USER_QUERY,
                &[&user.user_id, &user.username, &user.email],
            )
            .await?
        {
            Some(row) => Ok(row.try_into()?),
            None => Err(AccessModelError::NotFoundError),
        }
    }
}

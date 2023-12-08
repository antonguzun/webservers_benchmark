use crate::usecases::base_entities::AccessModelError;
use crate::usecases::users::entities::{User, UserForUpdate};
use crate::usecases::users::get_user::FindUserById;
use crate::usecases::users::user_updater::UpdateUser;
use async_trait::async_trait;
use chrono::NaiveDateTime;
use log::error;
use mysql_async::prelude::{FromRow, Queryable};
use mysql_async::{FromRowError, Pool, Row, from_value, from_value_opt};

pub struct UserRepo<'a> {
    db_pool: &'a Pool,
}

impl UserRepo<'_> {
    pub fn new<'a>(db_pool: &'a Pool) -> UserRepo {
        UserRepo { db_pool }
    }
}

fn take_value<T>(row: &Row, key_name: &str) -> Result<T, FromRowError>
where
    T: mysql_async::prelude::FromValue,
{
    row.get(key_name).ok_or_else(|| FromRowError(row.clone()))
}

impl From<mysql_async::Error> for AccessModelError {
    fn from(err: mysql_async::Error) -> AccessModelError {
        error!("Db error: {}", err);
        AccessModelError::FatalError
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
WHERE user_id=?
"#;

const UPDATE_USER_QUERY: &str = r#"
UPDATE users
SET
    username=?,
    email=?,
    updated_at=NOW()
WHERE user_id=?
RETURNING
    user_id,
    username,
    email,
    is_archived,
    created_at
"#;

impl FromRow for User {
    fn from_row_opt(row: Row) -> std::result::Result<Self, FromRowError> {
        let crated_at: NaiveDateTime = take_value(&row, "created_at")?;
        Ok(User {
            user_id: take_value(&row, "user_id")?,
            // user_id: from_value_opt(row.pop()),
            username: take_value(&row, "username")?,
            email: take_value(&row, "email")?,
            is_archived: take_value(&row, "is_archived")?,
            created_at: crated_at.to_string(),
        })
    }
}

#[async_trait]
impl FindUserById for UserRepo<'_> {
    async fn find_user_by_id(&self, user_id: i32) -> Result<User, AccessModelError> {
        let mut conn = self.db_pool.get_conn().await?;

        match conn
            .exec_first::<User, _, _>(GET_BY_ID_QUERY, (user_id,))
            .await?
        {
            Some(user) => Ok(user),
            None => Err(AccessModelError::NotFoundError),
        }
    }
}

#[async_trait]
impl UpdateUser for UserRepo<'_> {
    async fn update_user_in_storage(&self, user: UserForUpdate) -> Result<User, AccessModelError> {
        let mut conn = self.db_pool.get_conn().await?;

        conn.exec::<u32, _, _>(UPDATE_USER_QUERY, (user.username, user.email, user.user_id))
            .await?;

        match conn
            .exec_first::<User, _, _>(GET_BY_ID_QUERY, (user.user_id,))
            .await?
        {
            Some(user) => Ok(user),
            None => Err(AccessModelError::NotFoundError),
        }
    }
}

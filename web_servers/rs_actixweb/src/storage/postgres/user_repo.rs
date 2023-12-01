use crate::usecases::base_entities::AccessModelError;
use crate::usecases::users::entities::{User, UserForUpdate};
use crate::usecases::users::get_user::FindUserById;
use crate::usecases::users::user_updater::UpdateUser;
use async_trait::async_trait;
use deadpool_postgres::{Pool, PoolError};
use log::error;
use tokio_postgres::types::ToSql;
use tokio_postgres::Row;

pub trait SqlSerializer<T> {
    fn from_sql_result(row: &Row) -> T;
}

impl SqlSerializer<User> for User {
    fn from_sql_result(row: &Row) -> User {
        User::new(row.get(0), row.get(1), row.get(2), row.get(3), row.get(4))
    }
}

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

pub async fn exec_query<T: SqlSerializer<T>>(
    db_pool: &Pool,
    query: &str,
    params: &[&(dyn ToSql + Sync)],
) -> Result<T, AccessModelError> {
    let client = db_pool.get().await?;

    match client.query_opt(query, params).await? {
        Some(row) => Ok(T::from_sql_result(&row)),
        None => Err(AccessModelError::NotFoundError),
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

#[async_trait]
impl FindUserById for UserRepo<'_> {
    async fn find_user_by_id(&self, user_id: i32) -> Result<User, AccessModelError> {
        exec_query(&self.db_pool, GET_BY_ID_QUERY, &[&user_id]).await
    }
}

#[async_trait]
impl UpdateUser for UserRepo<'_> {
    async fn update_user_in_storage(&self, user: UserForUpdate) -> Result<User, AccessModelError> {
        exec_query(
            &self.db_pool,
            UPDATE_USER_QUERY,
            &[&user.user_id, &user.username, &user.email],
        )
        .await
    }
}

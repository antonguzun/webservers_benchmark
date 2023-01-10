use crate::storage::postgres::base::{get_item, update_item, SqlSerializer};

use crate::usecases::base_entities::AccessModelError;
use crate::usecases::users::entities::{User, UserForUpdate};
use crate::usecases::users::get_user::FindUserById;
use crate::usecases::users::user_updater::UpdateUser;
use async_trait::async_trait;
use deadpool_postgres::Pool;

use tokio_postgres::types::ToSql;
use tokio_postgres::Row;

pub struct UserRepo {
    db_pool: Pool,
}

impl UserRepo {
    pub fn new(db_pool: Pool) -> UserRepo {
        UserRepo { db_pool }
    }
}

const GET_BY_ID_QUERY: &str = "SELECT user_id, username, email, is_archived, created_at 
    FROM users 
    WHERE user_id=$1";

const UPDATE_USER_QUERY: &str = "UPDATE users 
    SET username=$2, email=$3, updated_at=NOW()
    WHERE user_id=$1 
    RETURNING user_id, username, email, is_archived, created_at";

impl SqlSerializer<User> for User {
    fn from_sql_result(row: &Row) -> User {
        User::new(row.get(0), row.get(1), row.get(2), row.get(3), row.get(4))
    }
}
#[async_trait]
impl FindUserById for UserRepo {
    async fn find_user_by_id(&self, user_id: i32) -> Result<User, AccessModelError> {
        get_item(&self.db_pool, GET_BY_ID_QUERY, &[&user_id]).await
    }
}

#[async_trait]
impl UpdateUser for UserRepo {
    async fn update_user_in_storage(&self, user: UserForUpdate) -> Result<User, AccessModelError> {
        let params: &[&(dyn ToSql + Sync)] = &[&user.user_id, &user.username, &user.email];
        update_item(&self.db_pool, UPDATE_USER_QUERY, params).await
    }
}

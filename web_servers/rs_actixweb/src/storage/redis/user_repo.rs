use crate::usecases::base_entities::AccessModelError;
use crate::usecases::users::entities::{User, UserForUpdate};
use crate::usecases::users::get_user::FindUserById;
use crate::usecases::users::user_updater::UpdateUser;
use async_trait::async_trait;
use log::error;
use redis::aio::ConnectionManager;
use redis::AsyncCommands;

pub struct UserRepo<'a> {
    db_pool: &'a ConnectionManager,
}

impl UserRepo<'_> {
    pub fn new<'a>(db_pool: &'a ConnectionManager) -> UserRepo {
        UserRepo { db_pool }
    }
}

#[async_trait]
impl FindUserById for UserRepo<'_> {
    async fn find_user_by_id(&self, user_id: i32) -> Result<User, AccessModelError> {
        let mut con = self.db_pool.clone();
        let raw_user: Option<String> = match con.get(format!("user_{}", user_id).to_string()).await
        {
            Ok(user) => user,
            Err(e) => {
                error!("redis fetching error: {}", e);
                return Err(AccessModelError::FatalError);
            }
        };
        match raw_user {
            Some(r_user) => match serde_json::from_str(&r_user) {
                Ok(user) => Ok(user),
                Err(e) => {
                    error!("redis corrupted data: {}", e);
                    error!("data: {}", r_user);
                    Err(AccessModelError::FatalError)
                }
            },
            None => Err(AccessModelError::NotFoundError),
        }
    }
}

#[async_trait]
impl UpdateUser for UserRepo<'_> {
    async fn update_user_in_storage(&self, user: UserForUpdate) -> Result<User, AccessModelError> {
        let mut user_dto = self.find_user_by_id(user.user_id).await?;
        user_dto.username = user.username;
        user_dto.email = Some(user.email);
        let mut con = self.db_pool.clone();
        let user_key = format!("user_{}", user.user_id);
        let user_to_save = match serde_json::to_string(&user_dto) {
            Ok(user) => user,
            Err(e) => {
                error!("redis serializing error: {}", e);
                return Err(AccessModelError::FatalError);
            }
        };
        let _: Option<String> = match con.set(user_key, user_to_save).await {
            Ok(_user) => _user,
            Err(e) => {
                error!("redis set error: {}", e);
                return Err(AccessModelError::FatalError);
            }
        };
        Ok(user_dto)
    }
}

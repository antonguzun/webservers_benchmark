use crate::usecases::base_entities::AccessModelError;
use crate::usecases::users::entities::{User, UserForUpdate};
use crate::usecases::users::errors::UserUCError;

use async_trait::async_trait;

#[async_trait]
pub trait UpdateUser {
    async fn update_user_in_storage(&self, user: UserForUpdate) -> Result<User, AccessModelError>;
}

pub async fn update_user(
    user_access_model: &impl UpdateUser,
    username: String,
    email: String,
    user_id: i32,
) -> Result<User, UserUCError> {
    let user_data = UserForUpdate {
        user_id,
        username,
        email,
    };
    match user_access_model.update_user_in_storage(user_data).await {
        Ok(user) => Ok(user),
        Err(AccessModelError::AlreadyExists) => Err(UserUCError::AlreadyExists),
        Err(AccessModelError::TemporaryError) => Err(UserUCError::TemporaryError),
        Err(_) => Err(UserUCError::FatalError),
    }
}

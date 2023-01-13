use crate::usecases::base_entities::AccessModelError;
use crate::usecases::users::entities::User;
use crate::usecases::users::errors::UserUCError;
use async_trait::async_trait;

#[async_trait]
pub trait FindUserById {
    async fn find_user_by_id(&self, user_id: i32) -> Result<User, AccessModelError>;
}

pub async fn get_user_by_id(
    user_repo: &impl FindUserById,
    user_id: i32,
) -> Result<User, UserUCError> {
    match user_repo.find_user_by_id(user_id).await {
        Ok(user) => Ok(user),
        Err(AccessModelError::NotFoundError) => Err(UserUCError::NotFoundError),
        Err(AccessModelError::TemporaryError) => Err(UserUCError::TemporaryError),
        Err(_) => Err(UserUCError::FatalError),
    }
}

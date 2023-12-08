use crate::usecases::base_entities::AccessModelError;
use crate::usecases::users::entities::User;
use async_trait::async_trait;

#[async_trait]
pub trait FindUserById {
    async fn find_user_by_id(&self, user_id: i32) -> Result<User, AccessModelError>;
}

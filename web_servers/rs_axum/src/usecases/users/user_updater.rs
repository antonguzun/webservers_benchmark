use crate::usecases::base_entities::AccessModelError;
use crate::usecases::users::entities::{User, UserForUpdate};

use async_trait::async_trait;

#[async_trait]
pub trait UpdateUser {
    async fn update_user_in_storage(&self, user: UserForUpdate) -> Result<User, AccessModelError>;
}

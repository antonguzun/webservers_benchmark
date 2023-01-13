use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct User {
    pub user_id: i32,
    pub username: String,
    pub email: Option<String>,
    pub is_archived: bool,
    pub created_at: String,
}

#[derive(Serialize, Deserialize)]
pub struct UserForUpdate {
    pub user_id: i32,
    pub username: String,
    pub email: String,
}

impl User {
    pub fn new(
        user_id: i32,
        username: String,
        email: Option<String>,
        is_archived: bool,
        created_at: DateTime<Utc>,
    ) -> User {
        User {
            user_id,
            username,
            email,
            is_archived,
            created_at: created_at.to_rfc3339(),
        }
    }
}

use axum::{
    extract::{Path, Query, Request, State},
    http::{self, StatusCode},
    middleware::{self, Next},
    response::{IntoResponse, Response},
    routing::{get, patch},
    Json, Router,
};
use bench::usecases::{
    base_entities::AccessModelError,
    users::{entities::UserForUpdate, get_user::FindUserById, user_updater::UpdateUser},
};
use http::header::HeaderValue;
use serde::{Deserialize, Serialize};
use std::sync::Arc;

#[cfg(feature = "db_mysql")]
use bench::common::mysql::{Config, Resources};
#[cfg(feature = "db_posgres_client_deadpool")]
use bench::common::postgres::{Config, Resources};
#[cfg(feature = "db_redis")]
use bench::common::redis::{Config, Resources};
#[cfg(feature = "db_mysql")]
use bench::storage::mysql::user_repo::UserRepo;
#[cfg(feature = "db_posgres_client_deadpool")]
use bench::storage::postgres::user_repo::UserRepo;
#[cfg(feature = "db_redis")]
use bench::storage::redis::user_repo::UserRepo;

struct ApiError(AccessModelError);

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status_code, error_message) = match self.0 {
            AccessModelError::NotFoundError => (StatusCode::NOT_FOUND, "User not found"),
            AccessModelError::AlreadyExists => (StatusCode::CONFLICT, "User already exists"),
            AccessModelError::TemporaryError => {
                (StatusCode::SERVICE_UNAVAILABLE, "Temporary error")
            }
            AccessModelError::FatalError => (StatusCode::INTERNAL_SERVER_ERROR, "Fatal error"),
        };
        (status_code, error_message).into_response()
    }
}

pub async fn get_user_by_id(
    Path(user_id): Path<i32>,
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    let user_repo = UserRepo::new(&state.resources.db_pool);
    match user_repo.find_user_by_id(user_id).await {
        Ok(user) => (StatusCode::OK, Json(user)).into_response(),
        Err(error) => ApiError(error).into_response(),
    }
}

#[derive(Deserialize, Serialize)]
pub struct UserUpdateScheme {
    pub email: String,
    pub username: String,
}

pub async fn update_user_handler(
    Path(user_id): Path<i32>,
    Json(payload): Json<UserUpdateScheme>,
    state: Arc<AppState>,
) -> Response {
    let user_data = UserForUpdate {
        user_id,
        username: payload.email.to_string(),
        email: payload.email.to_string(),
    };
    let user_access_model = UserRepo::new(&state.resources.db_pool);
    match user_access_model.update_user_in_storage(user_data).await {
        Ok(user) => (StatusCode::OK, Json(user)).into_response(),
        Err(error) => ApiError(error).into_response(),
    }
}

#[derive(Deserialize, Serialize)]
pub struct ParamsQuery {
    pub param1: String,
    pub param2: String,
    pub param3: String,
}

pub async fn plain_handler(Query(query): Query<ParamsQuery>) -> impl IntoResponse {
    let content = format!(
        "param1={};param2={};param3={}",
        query.param1, query.param2, query.param3
    );
    (StatusCode::OK, content)
}

pub async fn to_json_handler(Query(query): Query<ParamsQuery>) -> impl IntoResponse {
    (StatusCode::OK, Json(query))
}

pub async fn ping_handler() -> impl IntoResponse {
    (StatusCode::OK, "pong")
}

pub struct AppState {
    pub config: Config,
    pub resources: Resources,
}

async fn auth(req: Request, next: Next) -> Result<Response, StatusCode> {
    if req.headers().get("token") == Some(&HeaderValue::from_str("hardcoded_token").unwrap()) {
        Ok(next.run(req).await)
    } else {
        Err(StatusCode::UNAUTHORIZED)
    }
}

#[tokio::main]
async fn main() {
    let config = Config::create_config();
    let resources = Resources::create_resources(&config).await;

    let shared_state = Arc::new(AppState { config, resources });

    let private_api = Router::new()
        .route("/plain/", get(plain_handler))
        .route("/to_json/", get(to_json_handler))
        .route("/user/:user_id/", get(get_user_by_id))
        .route(
            "/user/:user_id/",
            patch({
                let shared_state = Arc::clone(&shared_state);
                move |path, json| update_user_handler(path, json, shared_state)
            }),
        )
        .route_layer(middleware::from_fn(auth));
    let app = Router::new()
        .route("/ping/", get(ping_handler))
        .nest("/", private_api)
        .with_state(shared_state);

    let listener = tokio::net::TcpListener::bind("127.0.0.1:8000")
        .await
        .unwrap();
    axum::serve(listener, app.into_make_service())
        .await
        .unwrap();
}

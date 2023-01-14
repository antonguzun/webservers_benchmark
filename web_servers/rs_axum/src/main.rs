use axum::{
    extract::{State, Path, Query},
    routing::{get},
    http::{self, Request, StatusCode},
    response::{IntoResponse, Response},
    Json, Router,
    middleware::{self, Next},
};
use http::header::{HeaderName, HeaderValue};
use serde::{Deserialize, Serialize};

use std::net::SocketAddr;
use std::sync::Arc;

use bench::common::{Config, Resources};
use bench::storage::postgres::user_repo::UserRepo;
use bench::usecases::users::{get_user, user_updater};


// pub async fn get_user_by_id(Path(user_id): Path<i32>, State(state): State<AppState>) -> impl IntoResponse {
//     let user_repo = UserRepo::new(&state.resources.db_pool);
//     let user = get_user::get_user_by_id(&user_repo, user_id).await.unwrap();
//     (StatusCode::OK, Json(user))
// }

// #[derive(Deserialize, Serialize)]
// pub struct UserUpdateScheme {
//     pub email: String,
//     pub username: String,
// }

// pub async fn update_user_handler(
//     Path(user_id): Path<i32>,
//     Json(payload): Json<UserUpdateScheme>,
//     State(state): State<AppState>,
// ) -> impl IntoResponse {
//     let username = payload.username.to_string();
//     let email = payload.email.to_string();
//     let user_access_model = UserRepo::new(&state.resources.db_pool);
//     let user = user_updater::update_user(&user_access_model, username, email, user_id).await.unwrap();
//     (StatusCode::OK, Json(user))
// }

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



struct AppState {
    config: Config,
    resources: Resources,
}

async fn auth<B>(mut req: Request<B>, next: Next<B>) -> Result<Response, StatusCode> {
    if req.headers().get("token") == Some(&HeaderValue::from_str("hardcoded_token").unwrap()) {
        Ok(next.run(req).await)
    } else {
        Err(StatusCode::UNAUTHORIZED)
    }

}
#[tokio::main(flavor = "current_thread")]
async fn main() {
    let config = Config::create_config();
    let resources = Resources::create_resources(&config).await;

    let shared_state = Arc::new(AppState { config, resources });

    let app = Router::new()
        .route("/ping/", get(ping_handler))
        .route("/plain/", get(plain_handler))
        .route("/to_json/", get(to_json_handler))
        // .route("/user/:user_id/", get(get_user_by_id).patch(update_user_handler))
        .with_state(shared_state)
        .route_layer(middleware::from_fn(auth));

    let addr = SocketAddr::from(([127, 0, 0, 1], 8000));
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}
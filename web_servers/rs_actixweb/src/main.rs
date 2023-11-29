use log::debug;
extern crate env_logger;
use actix_http::header::HeaderValue;
use actix_web::dev::Server;
use actix_web::guard::{Guard, GuardContext};
use actix_web::{web, App, HttpResponse, HttpServer, Responder};

#[cfg(feature = "db_mysql")] // TODO!(fix)
use bench::common::mysql::{Config, Resources};
#[cfg(feature = "db_posgres_client_deadpool")]
use bench::common::postgres::{Config, Resources};
#[cfg(feature = "db_redis")] // TODO!(fix)
use bench::common::redis::{Config, Resources};
#[cfg(feature = "db_mysql")] // TODO!(fix)
use bench::storage::mysql::user_repo::UserRepo;
#[cfg(feature = "db_posgres_client_deadpool")]
use bench::storage::postgres::user_repo::UserRepo;
#[cfg(feature = "db_redis")] // TODO!(fix)
use bench::storage::redis::user_repo::UserRepo;

use bench::usecases::users::errors::UserUCError;
use bench::usecases::users::{get_user, user_updater};
use log::error;
use serde::{Deserialize, Serialize};
use web::Data;

struct SimpleTokenChecker;

impl Guard for SimpleTokenChecker {
    fn check(&self, req: &GuardContext) -> bool {
        req.head().headers().get("token")
            == Some(&HeaderValue::from_str("hardcoded_token").unwrap())
    }
}

pub async fn get_user_by_id(user_id: web::Path<u32>, resources: Data<Resources>) -> impl Responder {
    let user_id = user_id.into_inner() as i32;
    let user_repo = UserRepo::new(&resources.db_pool);
    match get_user::get_user_by_id(&user_repo, user_id).await {
        Ok(user) => HttpResponse::Ok().json(user),
        Err(UserUCError::NotFoundError) => HttpResponse::NotFound().body("Not Found"),
        Err(_) => {
            error!("usecase error");
            HttpResponse::InternalServerError().body("internal error")
        }
    }
}

#[derive(Deserialize, Serialize)]
pub struct UserUpdateScheme {
    pub email: String,
    pub username: String,
}

pub async fn update_user_handler(
    user_id: web::Path<u32>,
    user_data: web::Json<UserUpdateScheme>,
    resources: Data<Resources>,
) -> impl Responder {
    let user_id = user_id.into_inner() as i32;
    let username = user_data.username.to_string();
    let email = user_data.email.to_string();
    let user_access_model = UserRepo::new(&resources.db_pool);
    match user_updater::update_user(&user_access_model, username, email, user_id).await {
        Ok(user) => HttpResponse::Ok().json(user),
        Err(_) => {
            error!("usecase error");
            HttpResponse::InternalServerError().body("internal error")
        }
    }
}

#[derive(Deserialize, Serialize)]
pub struct ParamsQuery {
    pub param1: String,
    pub param2: String,
    pub param3: String,
}

pub async fn plain_handler(query: web::Query<ParamsQuery>) -> impl Responder {
    HttpResponse::Ok().body(format!(
        "param1={};param2={};param3={}",
        query.param1, query.param2, query.param3
    ))
}

pub async fn to_json_handler(query: web::Query<ParamsQuery>) -> impl Responder {
    HttpResponse::Ok().json(query.into_inner())
}

pub async fn ping_handler() -> impl Responder {
    HttpResponse::Ok().body("success")
}

pub fn run_server(resources: Resources, config: Config) -> Result<Server, std::io::Error> {
    let server = HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(config.clone()))
            .app_data(web::Data::new(resources.clone()))
            .service(web::resource("/ping/").to(ping_handler))
            .service(
                web::resource("/user/{user_id}/")
                    .name("user")
                    .guard(SimpleTokenChecker)
                    .route(web::get().to(get_user_by_id))
                    .route(web::patch().to(update_user_handler)),
            )
            .service(
                web::resource("/plain/")
                    .name("plain")
                    .guard(SimpleTokenChecker)
                    .route(web::get().to(plain_handler)),
            )
            .service(
                web::resource("/to_json/")
                    .name("to_json")
                    .guard(SimpleTokenChecker)
                    .route(web::get().to(to_json_handler)),
            )
    })
    .bind("127.0.0.1:8000")?
    .run();
    Ok(server)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let config = Config::create_config();
    let resources = Resources::create_resources(&config).await;
    env_logger::init();
    debug!(target: "init", "{:#?}", config);
    run_server(resources, config)?.await
}

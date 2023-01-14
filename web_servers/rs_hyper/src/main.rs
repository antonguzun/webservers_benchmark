use http_body_util::{BodyExt, Full};
use hyper::body::Bytes;
use hyper::header::HeaderValue;
use hyper::server::conn::http1;

use hyper::service::Service;
use hyper::{body::Incoming as IncomingBody, Method, Request, Response, StatusCode};
use serde::{Deserialize, Serialize};

use tokio::net::TcpListener;

extern crate serde_qs as qs;

use std::future::Future;
use std::net::SocketAddr;
use std::pin::Pin;

use bench::common::{Config, Resources};
use bench::storage::postgres::user_repo::UserRepo;
use bench::usecases::users::errors::UserUCError;
use bench::usecases::users::{get_user, user_updater};

use lazy_static::lazy_static;
use regex::Regex;

lazy_static! {
    static ref USER_PATH_RE: Regex = Regex::new(r"hello (\w+)!").unwrap();
}

type GenericError = Box<dyn std::error::Error + Send + Sync>;
type Result<T> = std::result::Result<T, GenericError>;
type BoxBody = http_body_util::combinators::BoxBody<Bytes, hyper::Error>;

static INTERNAL_SERVER_ERROR: &[u8] = b"Internal Server Error";
static NOTFOUND: &[u8] = b"Not Found";
static FORBIDDEN: &[u8] = b"Forbidden";

async fn ping_handler() -> Result<Response<BoxBody>> {
    let response = Response::builder()
        .status(StatusCode::OK)
        .body(full("pong"))?;
    Ok(response)
}

pub async fn get_user_by_id(user_id: i32, resources: &Resources) -> Result<Response<BoxBody>> {
    let user_repo = UserRepo::new(&resources.db_pool);
    let response = match get_user::get_user_by_id(&user_repo, user_id).await {
        Ok(user) => Response::builder()
            .status(StatusCode::OK)
            .body(full(serde_json::to_string(&user)?))?,
        Err(UserUCError::NotFoundError) => Response::builder()
            .status(StatusCode::NOT_FOUND)
            .body(full(NOTFOUND))
            .unwrap(),
        Err(_) => {
            // error!("usecase error");
            Response::builder()
                .status(StatusCode::INTERNAL_SERVER_ERROR)
                .body(full(INTERNAL_SERVER_ERROR))
                .unwrap()
        }
    };
    Ok(response)
}

// #[derive(Deserialize, Serialize)]
// pub struct UserUpdateScheme {
//     pub email: String,
//     pub username: String,
// }

// pub async fn update_user_handler(
//     user_id: i32,
//     request: Request<IncomingBody>,
//     resources: Data<Resources>,
// ) -> impl Responder {
//     if request.headers().get("token") != Some(&HeaderValue::from_str("hardcoded_token").unwrap()) {
//         return Ok(Response::builder()
//             .status(StatusCode::FORBIDDEN)
//             .body(full(FORBIDDEN))
//             .unwrap());
//     }

//     let username = user_data.username.to_string();
//     let email = user_data.email.to_string();
//     let user_access_model = UserRepo::new(resources.db_pool.clone());
//     match user_updater::update_user(&user_access_model, username, email, user_id).await {
//         Ok(user) => HttpResponse::Ok().json(user),
//         Err(_) => {
//             error!("usecase error");
//             HttpResponse::InternalServerError().body("internal error")
//         }
//     }
// }

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct ParamsQuery {
    pub param1: String,
    pub param2: String,
    pub param3: String,
}

async fn plain_handler(request: Request<IncomingBody>) -> Result<Response<BoxBody>> {
    if request.headers().get("token") != Some(&HeaderValue::from_str("hardcoded_token").unwrap()) {
        return Ok(Response::builder()
            .status(StatusCode::FORBIDDEN)
            .body(full(FORBIDDEN))
            .unwrap());
    }

    let uri_string = request.uri().to_string();
    let params = uri_string.split("?").collect::<Vec<&str>>()[1];
    let query: ParamsQuery = qs::from_str(params).unwrap();

    let response = Response::builder()
        .status(StatusCode::OK)
        .body(full(format!(
            "param1={};param2={};param3={}",
            query.param1, query.param2, query.param3
        )))?;
    Ok(response)
}

async fn to_json_handler(request: Request<IncomingBody>) -> Result<Response<BoxBody>> {
    if request.headers().get("token") != Some(&HeaderValue::from_str("hardcoded_token").unwrap()) {
        return Ok(Response::builder()
            .status(StatusCode::FORBIDDEN)
            .body(full(FORBIDDEN))
            .unwrap());
    }

    let uri_string = request.uri().to_string();
    let params = uri_string.split("?").collect::<Vec<&str>>()[1];
    let query: ParamsQuery = qs::from_str(params)?;

    let response = Response::builder()
        .status(StatusCode::OK)
        .body(full(serde_json::to_string(&query)?))?;
    Ok(response)
}

fn full<T: Into<Bytes>>(chunk: T) -> BoxBody {
    Full::new(chunk.into())
        .map_err(|never| match never {})
        .boxed()
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> std::result::Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let addr: SocketAddr = ([127, 0, 0, 1], 8000).into();

    let listener = TcpListener::bind(addr).await?;
    println!("Listening on http://{}", addr);

    env_logger::init();

    loop {
        let (stream, _) = listener.accept().await?;
        tokio::task::spawn(async move {
            let config = Config::create_config();
            let resources = Resources::create_resources(&config).await;
            if let Err(err) = http1::Builder::new()
                // `service_fn` converts our function in a `Service`
                .serve_connection(stream, Srv { config, resources })
                .await
            {
                println!("Error serving connection: {:?}", err);
            }
        });
    }
}

struct Srv {
    config: Config,
    resources: Resources,
}

impl Service<Request<IncomingBody>> for Srv {
    type Response = Response<BoxBody>;
    type Error = GenericError;
    type Future =
        Pin<Box<dyn Future<Output = std::result::Result<Self::Response, Self::Error>> + Send>>;

    fn call(&mut self, req: Request<IncomingBody>) -> Self::Future {
        Box::pin(async {
            match (req.method(), req.uri().path()) {
                (&Method::GET, "/ping/") => ping_handler().await,
                (&Method::GET, "/plain/") => plain_handler(req).await,
                (&Method::GET, "/to_json/") => to_json_handler(req).await,
                _ => {
                    let user_id: Option<i32> = match USER_PATH_RE.captures(req.uri().path()) {
                        Some(caps) => match caps.get(0) {
                            Some(user_id_raw) => Some(user_id_raw.as_str().parse::<i32>().unwrap()),
                            None => None,
                        },
                        None => None,
                    };
                    match user_id {
                        Some(user_id) => {
                            match req.method() {
                                // &Method::GET => get_user_by_id(user_id, &self.resources).await,
                                // &Method::PATCH => {
                                //     // Return 200 OK response.
                                //     let response = Response::builder()
                                //         .status(StatusCode::OK)
                                //         .body(full(format!("user_id={}", user_id)))?;
                                //     return Ok(response);
                                // }
                                _ => {
                                    // Return 404 not found response.
                                    Ok(Response::builder()
                                        .status(StatusCode::NOT_FOUND)
                                        .body(full(NOTFOUND))
                                        .unwrap())
                                }
                            }
                        }
                        None => {
                            // Return 404 not found response.
                            Ok(Response::builder()
                                .status(StatusCode::NOT_FOUND)
                                .body(full(NOTFOUND))
                                .unwrap())
                        }
                    }
                }
            }
        })
    }
}

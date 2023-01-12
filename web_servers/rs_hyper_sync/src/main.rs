use http_body_util::{BodyExt, Full};
use hyper::body::Bytes;
use hyper::header::HeaderValue;
use hyper::server::conn::http1;
use hyper::service::service_fn;

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

fn ping_handler() -> Result<Response<BoxBody>> {
    let response = Response::builder()
        .status(StatusCode::OK)
        .body(full("pong"))?;
    Ok(response)
}


#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct ParamsQuery {
    pub param1: String,
    pub param2: String,
    pub param3: String,
}

fn plain_handler(request: Request<IncomingBody>) -> Result<Response<BoxBody>> {
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

fn to_json_handler(request: Request<IncomingBody>) -> Result<Response<BoxBody>> {
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

#[tokio::main]
async fn main() -> std::result::Result<(), Box<dyn std::error::Error>> {
    let addr: SocketAddr = ([127, 0, 0, 1], 8000).into();

    let listener = TcpListener::bind(addr).await?;
    println!("Listening on http://{}", addr);

    env_logger::init();

    loop {
        let (stream, _) = listener.accept().await?;
        let service = service_fn(move |req| 
            match (req.method(), req.uri().path()) {
                (&Method::GET, "/ping/") => ping_handler(),
                (&Method::GET, "/plain/") => plain_handler(req),
                (&Method::GET, "/to_json/") => to_json_handler(req),
                _ => {
                    Ok(Response::builder()
                                .status(StatusCode::NOT_FOUND)
                                .body(full(NOTFOUND))
                                .unwrap())
                    }
                }
        );


        if let Err(err) = http1::Builder::new()
        .serve_connection(stream, service)
            .await
        {
            println!("Error serving connection: {:?}", err);
        }
    }
}

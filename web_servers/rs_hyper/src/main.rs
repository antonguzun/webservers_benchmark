use hyper::body::Bytes;
use hyper::server::conn::http1;
use hyper::service::service_fn;
use hyper::service::Service;
use hyper::{body::Incoming as IncomingBody, header, Method, Request, Response, StatusCode};
use std::convert::Infallible;
use tokio::net::TcpListener;
use http_body_util::{BodyExt, Empty, Full};
use http::uri::Url;

use std::future::Future;
use std::net::SocketAddr;
use std::pin::Pin;
use std::sync::{
    atomic::{AtomicUsize, Ordering},
    Arc,
};

use bench::common::{Config, Resources};
use bench::storage::postgres::user_repo::UserRepo;
use bench::usecases::users::errors::UserUCError;
use bench::usecases::users::{get_user, user_updater};


type GenericError = Box<dyn std::error::Error + Send + Sync>;
type Result<T> = std::result::Result<T, GenericError>;
type BoxBody = http_body_util::combinators::BoxBody<Bytes, hyper::Error>;

static INTERNAL_SERVER_ERROR: &[u8] = b"Internal Server Error";
static NOTFOUND: &[u8] = b"Not Found";


async fn ping_handler() -> Result<Response<BoxBody>> {
    let response = Response::builder()
        .status(StatusCode::OK)
        .body(full("pong"))?;
    Ok(response)}

// #[derive(Deserialize, Serialize)]
// pub struct ParamsQuery {
//     pub param1: String,
//     pub param2: String,
//     pub param3: String,
// }

async fn plain_handler(request: Request<IncomingBody>) -> Result<Response<BoxBody>> {
    let params = Url::parse(&request.uri().to_string()).unwrap().query_pairs();

    let response = Response::builder()
        .status(StatusCode::OK)
        .body(full("pong"))?;
    Ok(response)}
    
async fn to_json_handler(request: Request<IncomingBody>) -> Result<Response<BoxBody>> {
    let params = Url::parse(&request.uri().to_string()).unwrap().query_pairs();

        let response = Response::builder()
            .status(StatusCode::OK)
            .body(full("pong"))?;
        Ok(response)}
    
    
        
async fn router(request: Request<IncomingBody>, resources: &Resources) -> Result<Response<BoxBody>> {
    match (request.method(), request.uri().path()) {
        (&Method::GET, "/ping/") => ping_handler().await,
        (&Method::GET, "/plain/") => plain_handler(request).await,
        (&Method::GET, "/to_json/") => to_json_handler(request).await,
        // (&Method::GET, "/user/") => client_request_response().await,
        // (&Method::PATCH, "/user/") => client_request_response().await,
        _ => {
            // Return 404 not found response.
            Ok(Response::builder()
                .status(StatusCode::NOT_FOUND)
                .body(full(NOTFOUND))
                .unwrap())
        }
    }
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

    let config = Config::create_config();
    let resources = Resources::create_resources(&config).await;
    env_logger::init();

    loop {
        let (stream, _) = listener.accept().await?;
        let resources = Arc::new(resources.clone());
        let service = service_fn(move |req| {
            let resources = Arc::new(resources.clone());
            async move {
                router(req, &resources).await
            }
        });
        if let Err(err) = http1::Builder::new()
            .serve_connection(stream, service)
            .await
        {
            println!("Error serving connection: {:?}", err);
        }
        // tokio::task::spawn(async move {
        //     if let Err(err) = http1::Builder::new()
        //         .serve_connection(stream, service)
        //         .await
        //     {
        //         println!("Error serving connection: {:?}", err);
        //     }
        // });
    }
}

#[cfg(all(feature = "db_posgres_client_deadpool", feature = "db_redis"))]
compile_error!("feature \"db_posgres_client_deadpool\" and feature \"redis\" cannot be enabled at the same time");
#[cfg(feature = "db_posgres_client_deadpool")]
pub mod postgres;
#[cfg(feature = "db_redis")]
pub mod redis;

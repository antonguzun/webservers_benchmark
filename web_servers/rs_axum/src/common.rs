#[cfg(all(
    feature = "db_posgres_client_deadpool",
    feature = "db_redis",
    feature = "db_mysql"
))]
compile_error!("feature \"db_posgres_client_deadpool\" and feature \"redis\" and \"db_mysql\" cannot be enabled at the same time");
#[cfg(all(feature = "db_posgres_client_deadpool", feature = "db_redis"))]
compile_error!("feature \"db_posgres_client_deadpool\" and feature \"redis\" cannot be enabled at the same time");
#[cfg(all(feature = "db_mysql", feature = "db_redis"))]
compile_error!("feature \"db_mysql\" and feature \"redis\" cannot be enabled at the same time");
#[cfg(all(feature = "db_posgres_client_deadpool", feature = "db_mysql"))]
compile_error!("feature \"db_posgres_client_deadpool\" and feature \"db_mysql\" cannot be enabled at the same time");
pub mod mysql;
pub mod postgres;
pub mod redis;

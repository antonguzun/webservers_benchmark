use redis::aio::ConnectionManager;
use redis::Client;

#[derive(Clone, Debug)]
pub struct DbConfig {
    pub dsn: String,
}

#[derive(Clone, Debug)]
pub struct SecurityConfig {
    pub secret_key: String,
}

#[derive(Clone, Debug)]
pub struct Config {
    pub database_config: DbConfig,
    pub security_config: SecurityConfig,
    pub service_name: String,
}

impl Config {
    pub fn create_config() -> Config {
        Config {
            database_config: DbConfig {
                dsn: "redis://localhost:26379".to_string(),
            },
            security_config: SecurityConfig {
                secret_key: "asdsadsd".to_string(),
            },
            service_name: "bench".to_string(),
        }
    }
}

#[derive(Clone)]
pub struct Resources {
    pub db_pool: ConnectionManager,
}

impl Resources {
    pub async fn create_resources(config: &Config) -> Resources {
        let db_pool = create_pool(&config).await;
        Resources { db_pool }
    }
}

async fn create_pool(config: &Config) -> ConnectionManager {
    let client = Client::open(config.database_config.dsn.clone()).unwrap();
    let conn = client.get_tokio_connection_manager().await.unwrap();
    conn
}

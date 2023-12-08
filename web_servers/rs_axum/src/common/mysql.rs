use mysql_async::Pool;

#[derive(Clone, Debug)]
pub struct Config {
    pub dsn: String,
}

impl Config {
    pub fn create_config() -> Config {
        Config {
            dsn:
                "fake FIXME!".to_owned(),
        }
    }
}

#[derive(Clone)]
pub struct Resources {
    pub db_pool: Pool,
}

impl Resources {
    pub async fn create_resources(config: &Config) -> Resources {
        let db_pool: Pool = create_pool(&config);
        Resources { db_pool }
    }
}

fn create_pool(_config: &Config) -> Pool {
    let pool = Pool::new("mysql://user:pass@localhost:13306/webservers_bench");
    pool
}

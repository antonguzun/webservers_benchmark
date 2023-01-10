use crate::usecases::base_entities::AccessModelError;
use deadpool_postgres::{Client, Pool};
use log::error;
use tokio_postgres::types::ToSql;
use tokio_postgres::{Row, Statement};

pub async fn get_client(db_pool: &Pool) -> Result<Client, AccessModelError> {
    match db_pool.get().await {
        Ok(client) => Ok(client),
        Err(e) => {
            error!("{}", e);
            Err(AccessModelError::TemporaryError)
        }
    }
}

pub async fn prepare_stmt(client: &Client, query: &str) -> Result<Statement, AccessModelError> {
    match client.prepare(query).await {
        Ok(stmt) => Ok(stmt),
        Err(e) => {
            error!("{}", e);
            Err(AccessModelError::FatalError)
        }
    }
}

pub trait SqlSerializer<T> {
    fn from_sql_result(row: &Row) -> T;
}

pub async fn get_item<T: SqlSerializer<T>>(
    db_pool: &Pool,
    query: &str,
    params: &[&(dyn ToSql + Sync)],
) -> Result<T, AccessModelError> {
    let client = get_client(db_pool).await?;
    let stmt = prepare_stmt(&client, query).await?;
    match client.query(&stmt, params).await {
        Ok(rows) if rows.len() == 1 => Ok(T::from_sql_result(&rows[0])),
        Ok(rows) if rows.len() == 0 => Err(AccessModelError::NotFoundError),
        Ok(_) => {
            error!("During getting item count of retirning rows not equals one");
            Err(AccessModelError::FatalError)
        }
        Err(e) => {
            error!("{}", e);
            Err(AccessModelError::FatalError)
        }
    }
}

pub async fn update_item<T: SqlSerializer<T>>(
    db_pool: &Pool,
    query: &str,
    params: &[&(dyn ToSql + Sync)],
) -> Result<T, AccessModelError> {
    let client = get_client(db_pool).await?;
    let stmt = prepare_stmt(&client, query).await?;
    match client.query(&stmt, params).await {
        Ok(rows) if rows.len() == 1 => Ok(T::from_sql_result(&rows[0])),
        Ok(rows) if rows.len() == 0 => Err(AccessModelError::NotFoundError),
        Ok(_) => {
            error!("During update item count of retirning rows not equals one");
            Err(AccessModelError::FatalError)
        }
        Err(e) => {
            error!("{}", e);
            Err(AccessModelError::FatalError)
        }
    }
}

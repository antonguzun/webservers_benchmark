package mysql

import (
	"database/sql"
	"go_fasthttp/storage"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

type MysqlUserRepo struct {
	db *sql.DB
}

const GET_USER_BY_ID_QUERY = "SELECT user_id, username, email, is_archived, created_at FROM users WHERE user_id=?"
const UPDATE_USER_QUERY = "UPDATE users SET username=?, email=?, updated_at=NOW() WHERE user_id=?"

func (repo MysqlUserRepo) GetUserById(user_id int) (*storage.User, error) {
	var user storage.User

	row := repo.db.QueryRow(GET_USER_BY_ID_QUERY, user_id)
	err := row.Scan(&user.UserID, &user.Username, &user.Email, &user.IsArchived, &user.CreatedAt)
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (repo MysqlUserRepo) UpdateUser(user_id int, userUpdate storage.UserUpdate) (*storage.User, error) {
	_, err := repo.db.Exec(UPDATE_USER_QUERY, userUpdate.Username, userUpdate.Email, user_id)
	if err != nil {
		return nil, err
	}
	return repo.GetUserById(user_id)
}

func CreateMysqlUserRepo() (*MysqlUserRepo, error) {
	db, err := sql.Open("mysql", "user:pass@tcp(localhost:13306)/webservers_bench?charset=utf8mb4&parseTime=true")
	if err != nil {
		return nil, err
	}
	db.SetConnMaxLifetime(time.Minute * 60)
	db.SetMaxOpenConns(80)
	db.SetMaxIdleConns(80)
	return &MysqlUserRepo{db: db}, nil
}

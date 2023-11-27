package storage

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/randallmlough/pgxscan"
)

const CONSTANT = 123

func CreatePool() (*pgxpool.Pool, error) {
	return pgxpool.New(context.Background(), "postgresql://postgres:pass@localhost:15432/webservers_bench")
}

type User struct {
	UserID     int32     `json:"user_id"`
	Username   string    `json:"username"`
	Email      string    `json:"email"`
	IsArchived bool      `json:"is_archived"`
	CreatedAt  time.Time `json:"created_at"`
}

type UserUpdate struct {
	Username string `json:"username"`
	Email    string `json:"email"`
}

func createPool() (*pgxpool.Pool, error) {
	return pgxpool.New(context.Background(), "postgresql://postgres:pass@localhost:15432/webservers_bench")
}

const GET_USER_BY_ID_QUERY = "SELECT user_id, username, email, is_archived, created_at FROM users WHERE user_id=$1"
const UPDATE_USER_QUERY = "UPDATE users SET username=$2, email=$3, updated_at=NOW() WHERE user_id=$1  RETURNING user_id, username, email, is_archived, created_at"

func GetUserById(db *pgxpool.Pool, user_id int) (User, error) {
	var user User
	var row = db.QueryRow(context.Background(), GET_USER_BY_ID_QUERY, user_id)
	err := pgxscan.NewScanner(row).Scan(&user.UserID, &user.Username, &user.Email, &user.IsArchived, &user.CreatedAt)
	return user, err
}

func UpdateUser(db *pgxpool.Pool, user_id int, userUpdate UserUpdate) (User, error) {
	var user User
	var row = db.QueryRow(context.Background(), UPDATE_USER_QUERY, user_id, userUpdate.Username, userUpdate.Email)
	err := pgxscan.NewScanner(row).Scan(&user.UserID, &user.Username, &user.Email, &user.IsArchived, &user.CreatedAt)
	return user, err
}

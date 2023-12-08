package postgres

import (
	"context"
	"go_gin/storage"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/randallmlough/pgxscan"
)

type PostgresUserRepo struct {
	db *pgxpool.Pool
}

const GET_USER_BY_ID_QUERY = `
	SELECT
		user_id,
		username,
		email,
		is_archived,
		created_at
	FROM users
	WHERE user_id=$1
`

const UPDATE_USER_QUERY = `
	UPDATE users
	SET
		username=$2,
		email=$3,
		updated_at=NOW()
	WHERE user_id=$1
	RETURNING
		user_id,
		username,
		email,
		is_archived,
		created_at
`

func (repo PostgresUserRepo) GetUserById(user_id int) (*storage.User, error) {
	var user storage.User
	var row = repo.db.QueryRow(
		context.Background(), GET_USER_BY_ID_QUERY, user_id,
	)
	err := pgxscan.NewScanner(row).Scan(
		&user.UserID, &user.Username, &user.Email, &user.IsArchived, &user.CreatedAt,
	)
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (repo PostgresUserRepo) UpdateUser(
	user_id int,
	userUpdate storage.UserUpdate,
) (*storage.User, error) {
	var user storage.User
	var row = repo.db.QueryRow(
		context.Background(), UPDATE_USER_QUERY, user_id, userUpdate.Username, userUpdate.Email,
	)
	err := pgxscan.NewScanner(row).Scan(
		&user.UserID, &user.Username, &user.Email, &user.IsArchived, &user.CreatedAt,
	)
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func CreatePostgresUserRepo() (*PostgresUserRepo, error) {
	db, err := pgxpool.New(
		context.Background(),
		"postgresql://postgres:pass@localhost:15432/webservers_bench?pool_max_conns=80",
	)
	if err != nil {
		return nil, err
	}
	return &PostgresUserRepo{db: db}, nil
}

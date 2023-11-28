package storage

import (
	"time"
)

type UserRepo interface {
	GetUserById(user_id int) (*User, error)
	UpdateUser(user_id int, userUpdate UserUpdate) (*User, error)
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

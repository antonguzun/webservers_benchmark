package redis

import (
	"context"
	"encoding/json"
	"fmt"
	"go_fasthttp/storage"
	"log"

	"github.com/redis/go-redis/v9"
)

var ctx = context.Background()

type RedisUserRepo struct {
	client *redis.Client
}

func userKey(user_id int) string {
	return fmt.Sprintf("user_%v", user_id)
}

func (repo RedisUserRepo) GetUserById(user_id int) (*storage.User, error) {
	var user storage.User
	key := userKey(user_id)

	val, err := repo.client.Get(ctx, key).Result()

	if err != nil {
		log.Println("get user error %v", user_id)
		return nil, err
	}

	err = json.Unmarshal([]byte(val), &user)
	if err != nil {
		return nil, err
	}

	return &user, nil
}

func (repo RedisUserRepo) UpdateUser(user_id int, userUpdate storage.UserUpdate) (*storage.User, error) {
	user, err := repo.GetUserById(user_id)

	if err != nil {
		return nil, err
	}

	user.Username = userUpdate.Username
	user.Email = userUpdate.Email

	key := userKey(user_id)
	val, err := json.Marshal(user)
	if err != nil {
		return nil, err
	}
	err = repo.client.Set(ctx, key, val, 0).Err()
	if err != nil {
		return nil, err
	}

	return user, nil
}

func CreateRedisUserRepo() (*RedisUserRepo, error) {
	opt, err := redis.ParseURL("redis://localhost:26379")
	if err != nil {
		return nil, err
	}
	client := redis.NewClient(opt)
	return &RedisUserRepo{client: client}, nil
}

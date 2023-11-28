package main

import (
	"errors"
	"log"
	"os"

	"go_gin/api"
	"go_gin/storage"
	"go_gin/storage/mysql"
	"go_gin/storage/postgres"
	"go_gin/storage/redis"

	"github.com/gin-gonic/gin"
)

func DbMiddleware(repo storage.UserRepo) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Set("databaseConn", repo)
		c.Next()
	}
}

func pingHandler(c *gin.Context) {
	c.String(200, "pong")
}

func main() {
	r := gin.Default()
	database_type := os.Getenv("DATABASE")

	var repo storage.UserRepo
	var err error

	if database_type == "postgres_raw" {
		repo, err = postgres.CreatePostgresUserRepo()
	} else if database_type == "mysql_raw" {
		repo, err = mysql.CreateMysqlUserRepo()
	} else if database_type == "redis" {
		repo, err = redis.CreateRedisUserRepo()
	} else {
		repo = nil
		err = errors.New("DATABASE env is not set properly")
	}
	if err != nil {
		log.Fatal(err)
	}

	r.Use(DbMiddleware(repo))
	r.GET("/ping/", pingHandler)
	r.GET("/plain/", api.PlainHandler)
	r.GET("/to_json/", api.ToJsonHandler)
	r.GET("/user/:user_id/", api.GetUserByIdHandler)
	r.PATCH("/user/:user_id/", api.UpdateUserHandler)

	log.Println("Gin server is starting...")

	r.Run("localhost:8000")
}

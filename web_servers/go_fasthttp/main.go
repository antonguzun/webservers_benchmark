package main

import (
	"errors"
	"log"
	"os"

	"go_fasthttp/api"
	"go_fasthttp/storage"
	"go_fasthttp/storage/mysql"
	"go_fasthttp/storage/postgres"
	"go_fasthttp/storage/redis"

	"github.com/fasthttp/router"
	"github.com/valyala/fasthttp"
)

func pingHandler(c *fasthttp.RequestCtx) {
	c.SetBodyString("pong")
}

func main() {
	r := router.New()
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
	handler := api.NewHandler(repo)

	r.GET("/ping/", pingHandler)
	r.GET("/plain/", api.Auth(api.PlainHandler))
	r.GET("/to_json/", api.Auth(api.ToJsonHandler))
	r.GET("/user/{user_id}/", api.Auth(handler.GetUserHandler))
	r.PATCH("/user/{user_id}/", api.Auth(handler.UpdateUserHandler))

	log.Println("Fasthttp server is starting...")

	fasthttp.ListenAndServe(":8000", r.Handler)
}

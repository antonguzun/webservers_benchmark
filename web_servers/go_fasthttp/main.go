package main

import (
	"log"

	"go_fasthttp/api"
	"go_fasthttp/storage"

	"github.com/fasthttp/router"
	"github.com/valyala/fasthttp"
)

func pingHandler(c *fasthttp.RequestCtx) {
	c.SetBodyString("pong")
}

func main() {
	r := router.New()

	db, err := storage.CreatePool()
	if err != nil {
		log.Fatal(err)
	}
	handler := api.NewHandler(db)

	r.GET("/ping/", pingHandler)
	r.GET("/plain/", api.Auth(api.PlainHandler))
	r.GET("/to_json/", api.Auth(api.ToJsonHandler))
	r.GET("/user/{user_id}/", api.Auth(handler.GetUserHandler))
	r.PATCH("/user/{user_id}/", api.Auth(handler.UpdateUserHandler))

	log.Println("Server is starting...")

	fasthttp.ListenAndServe(":8000", r.Handler)
}

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strconv"
	"time"

	"github.com/fasthttp/router"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/randallmlough/pgxscan"
	"github.com/valyala/fasthttp"
)

type Query struct {
	param1 string
	param2 string
	param3 string
}

func (u Query) MarshalJSON() ([]byte, error) {
	return json.Marshal(&struct {
		Param1 string `json:"param1"`
		Param2 string `json:"param2"`
		Param3 string `json:"param3"`
	}{
		Param1: u.param1,
		Param2: u.param2,
		Param3: u.param3,
	})
}

type User struct {
	user_id     int32
	username    string
	email       string
	is_archived bool
	created_at  time.Time
}

func (u User) MarshalJSON() ([]byte, error) {
	return json.Marshal(&struct {
		User_id     int32     `json:"user_id"`
		Username    string    `json:"username"`
		Email       string    `json:"email"`
		Is_archived bool      `json:"is_archived"`
		Created_at  time.Time `json:"created_at"`
	}{
		User_id:     u.user_id,
		Username:    u.username,
		Email:       u.email,
		Is_archived: u.is_archived,
		Created_at:  u.created_at,
	})
}

type UserUpdate struct {
	Username string `json:"username"`
	Email    string `json:"email"`
}

func create_pool() (*pgxpool.Pool, error) {
	return pgxpool.New(context.Background(), "postgresql://postgres:pass@localhost:15432/webservers_bench")
}

type Handler struct {
	db *pgxpool.Pool
}

func NewHandler(db *pgxpool.Pool) *Handler {
	return &Handler{db: db}
}

func Auth(requestHandler fasthttp.RequestHandler) fasthttp.RequestHandler {
	return func(c *fasthttp.RequestCtx) {
		headerValue := c.Request.Header.Peek("token")
		token := string(headerValue)
		if token == "hardcoded_token" {
			requestHandler(c)
		} else {
			c.Error("Forbidden", 403)
		}
	}
}

func main() {
	r := router.New()

	db, err := create_pool()
	if err != nil {
		log.Fatal(err)
	}
	handler := NewHandler(db)

	r.GET("/ping/", ping_handler)
	r.GET("/plain/", Auth(plain_handler))
	r.GET("/to_json/", Auth(to_json_handler))
	r.GET("/user/{user_id}/", Auth(handler.getUserHandler))
	r.PATCH("/user/{user_id}/", Auth(handler.update_user_handler))

	log.Println("Server is starting...")

	fasthttp.ListenAndServe(":8000", r.Handler)
}

func (h *Handler) getUserHandler(c *fasthttp.RequestCtx) {
	user_id := c.UserValue("user_id")
	user_id, err := strconv.Atoi(fmt.Sprintf("%v", user_id))
	if err != nil {
		c.Error("User Not Found", 404)
		return
	}
	var user User
	var row = h.db.QueryRow(context.Background(), "SELECT user_id, username, email, is_archived, created_at FROM users WHERE user_id=$1", user_id)

	if err := pgxscan.NewScanner(row).Scan(&user.user_id, &user.username, &user.email, &user.is_archived, &user.created_at); err != nil {
		log.Println(err)
		c.Error("Internal Server Error", fasthttp.StatusInternalServerError)
		return
	}

	jsonData, err := json.Marshal(user)
	if err != nil {
		c.Error("Error encoding JSON", fasthttp.StatusInternalServerError)
		return
	}

	c.SetContentType("application/json")
	c.Write(jsonData)
}

func (h *Handler) update_user_handler(c *fasthttp.RequestCtx) {
	user_id := c.UserValue("user_id")
	user_id, err := strconv.Atoi(fmt.Sprintf("%v", user_id))
	if err != nil {
		c.Error("User Not Found", 404)
		return
	}

	var update_data UserUpdate

	if err := json.Unmarshal(c.PostBody(), &update_data); err != nil {
		log.Println("decode get update_data json req err", err)
		c.Error("Bad Request", 400)
		return
	}
	if update_data.Username == "" || update_data.Email == "" {
		log.Println("username:", update_data.Username)
		log.Println("email:", update_data.Email)
		c.Error("Bad Request", 400)
		return
	}
	var user User
	var row = h.db.QueryRow(context.Background(), "UPDATE users  SET username=$2, email=$3, updated_at=NOW() WHERE user_id=$1  RETURNING user_id, username, email, is_archived, created_at", user_id, update_data.Username, update_data.Email)

	if err := pgxscan.NewScanner(row).Scan(&user.user_id, &user.username, &user.email, &user.is_archived, &user.created_at); err != nil {
		log.Println(err)
		c.Error("Internal Server Error", fasthttp.StatusInternalServerError)
		return
	}
	jsonData, err := json.Marshal(user)
	if err != nil {
		c.Error("Error encoding JSON", fasthttp.StatusInternalServerError)
		return
	}

	c.SetContentType("application/json")
	c.Write(jsonData)
}

func ping_handler(c *fasthttp.RequestCtx) {
	c.SetBodyString("pong")
}

func parse_params(c *fasthttp.RequestCtx) Query {
	params := c.QueryArgs()
	param1 := params.Peek("param1")
	param2 := params.Peek("param2")
	param3 := params.Peek("param3")

	return Query{string(param1), string(param2), string(param3)}
}

func plain_handler(c *fasthttp.RequestCtx) {
	query := parse_params(c)

	res := fmt.Sprintf("param1=%s; param2=%s, param3=%s", query.param1, query.param2, query.param3)
	c.SetBodyString(res)
}

func to_json_handler(c *fasthttp.RequestCtx) {
	query := parse_params(c)

	jsonData, err := json.Marshal(query)
	if err != nil {
		c.Error("Error encoding JSON", fasthttp.StatusInternalServerError)
		return
	}

	c.SetContentType("application/json")
	c.Write(jsonData)
}

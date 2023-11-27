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
	Param1 string `json:"param1"`
	Param2 string `json:"param2"`
	Param3 string `json:"param3"`
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

	db, err := createPool()
	if err != nil {
		log.Fatal(err)
	}
	handler := NewHandler(db)

	r.GET("/ping/", pingHandler)
	r.GET("/plain/", Auth(plainHandler))
	r.GET("/to_json/", Auth(toJsonHandler))
	r.GET("/user/{user_id}/", Auth(handler.getUserHandler))
	r.PATCH("/user/{user_id}/", Auth(handler.updateUserHandler))

	log.Println("Server is starting...")

	fasthttp.ListenAndServe(":8000", r.Handler)
}

func dumpData(c *fasthttp.RequestCtx, data interface{}) {
	jsonData, err := json.Marshal(data)
	if err != nil {
		c.Error("Error encoding JSON", fasthttp.StatusInternalServerError)
		return
	}

	c.SetContentType("application/json")
	c.Response.SetStatusCode(fasthttp.StatusOK)
	c.Write(jsonData)
}

func parseUserID(c *fasthttp.RequestCtx) (int, error) {
	user_id_raw := c.UserValue("user_id")
	user_id, err := strconv.Atoi(fmt.Sprintf("%v", user_id_raw))
	if err != nil {
		return 0, err
	}
	return user_id, nil
}

func (h *Handler) getUserHandler(c *fasthttp.RequestCtx) {
	user_id, err := parseUserID(c)
	if err != nil {
		c.Error("User Not Found", 404)
		return
	}

	var user User
	var row = h.db.QueryRow(context.Background(), "SELECT user_id, username, email, is_archived, created_at FROM users WHERE user_id=$1", user_id)

	if err := pgxscan.NewScanner(row).Scan(&user.UserID, &user.Username, &user.Email, &user.IsArchived, &user.CreatedAt); err != nil {
		log.Println(err)
		c.Error("Internal Server Error", fasthttp.StatusInternalServerError)
		return
	}

	dumpData(c, user)
}

func (h *Handler) updateUserHandler(c *fasthttp.RequestCtx) {
	user_id, err := parseUserID(c)
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

	if err := pgxscan.NewScanner(row).Scan(&user.UserID, &user.Username, &user.Email, &user.IsArchived, &user.CreatedAt); err != nil {
		log.Println(err)
		c.Error("Internal Server Error", fasthttp.StatusInternalServerError)
		return
	}
	dumpData(c, user)
}

func pingHandler(c *fasthttp.RequestCtx) {
	c.SetBodyString("pong")
}

func parseParams(c *fasthttp.RequestCtx) Query {
	params := c.QueryArgs()
	param1 := params.Peek("param1")
	param2 := params.Peek("param2")
	param3 := params.Peek("param3")

	return Query{string(param1), string(param2), string(param3)}
}

func plainHandler(c *fasthttp.RequestCtx) {
	query := parseParams(c)

	res := fmt.Sprintf("param1=%s; param2=%s, param3=%s", query.Param1, query.Param2, query.Param3)
	c.SetBodyString(res)
}

func toJsonHandler(c *fasthttp.RequestCtx) {
	query := parseParams(c)

	dumpData(c, query)
}

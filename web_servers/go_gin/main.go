package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/randallmlough/pgxscan"
)

type Query struct {
	param1 string
	param2 string
	param3 string
}
type User struct {
	user_id     int32
	username    string
	email       string
	is_archived bool
	created_at  time.Time
}

type UserUpdate struct {
	Username string `json:"username"`
	Email    string `json:"email"`
}

func DbMiddleware(db *pgxpool.Pool) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Set("databaseConn", db)
		c.Next()
	}
}

func create_pool() (*pgxpool.Pool, error) {
	return pgxpool.New(context.Background(), "postgresql://postgres:pass@localhost:15432/webservers_bench")
}

func main() {
	r := gin.Default()
	db, err := create_pool()
	if err != nil {
		log.Fatal(err)
	}

	r.Use(DbMiddleware(db))
	r.GET("/ping/", ping_handler)
	r.GET("/plain/", plain_handler)
	r.GET("/to_json/", to_json_handler)
	r.GET("/user/:user_id/", get_user_handler)
	r.PATCH("/user/:user_id/", update_user_handler)
	r.Run("localhost:8000")
}

func get_user_handler(c *gin.Context) {
	token := c.GetHeader("token")
	if token != "hardcoded_token" {
		c.String(403, "Forbidden")
		return
	}
	user_id, err := strconv.Atoi(c.Param("user_id"))
	if err != nil {
		c.String(404, "Not Found")
		return
	}
	db := c.MustGet("databaseConn").(*pgxpool.Pool)
	var user User
	var row = db.QueryRow(context.Background(), "SELECT user_id, username, email, is_archived, created_at FROM users WHERE user_id=$1", user_id)

	if err := pgxscan.NewScanner(row).Scan(&user.user_id, &user.username, &user.email, &user.is_archived, &user.created_at); err != nil {
		c.String(500, "Internal Server Error")
		log.Println(err)
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"user_id":     user.user_id,
		"username":    user.username,
		"email":       user.email,
		"is_archived": user.is_archived,
		"created_at":  user.created_at,
	})
}

func update_user_handler(c *gin.Context) {
	token := c.GetHeader("token")
	if token != "hardcoded_token" {
		c.String(403, "Forbidden")
		return
	}
	user_id, err := strconv.Atoi(c.Param("user_id"))
	if err != nil {
		c.String(404, "Not Found")
		return
	}
	var update_data UserUpdate

	if err := c.ShouldBindJSON(&update_data); err != nil {
		log.Println("decode get update_data json req err", err)
		c.String(400, "Bad Request")
		return
	}
	if update_data.Username == "" || update_data.Email == "" {
		log.Println("username:", update_data.Username)
		log.Println("email:", update_data.Email)
		c.String(400, "Bad Request")
		return
	}
	db := c.MustGet("databaseConn").(*pgxpool.Pool)
	var user User
	var row = db.QueryRow(context.Background(), "UPDATE users  SET username=$2, email=$3, updated_at=NOW() WHERE user_id=$1  RETURNING user_id, username, email, is_archived, created_at", user_id, update_data.Username, update_data.Email)

	if err := pgxscan.NewScanner(row).Scan(&user.user_id, &user.username, &user.email, &user.is_archived, &user.created_at); err != nil {
		c.String(500, "Internal Server Error")
		log.Println(err)
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"user_id":     user.user_id,
		"username":    user.username,
		"email":       user.email,
		"is_archived": user.is_archived,
		"created_at":  user.created_at,
	})
}

func ping_handler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"message": "pong",
	})
}

func plain_handler(c *gin.Context) {
	var query Query
	token := c.GetHeader("token")
	if token != "hardcoded_token" {
		c.String(403, "Forbidden")
		return
	}
	if c.ShouldBind(&query) != nil {
		c.String(400, "Bad Request")
		return
	}
	res := fmt.Sprintf("param1=%s; param2=%s, param3=%s", query.param1, query.param2, query.param3)
	c.String(http.StatusOK, res)
}

func to_json_handler(c *gin.Context) {
	var query Query
	token := c.GetHeader("token")
	if token != "hardcoded_token" {
		c.String(403, "Forbidden")
		return
	}
	if c.ShouldBind(&query) == nil {
		log.Println(query.param1)
		log.Println(query.param2)
		log.Println(query.param3)
	}
	c.JSON(http.StatusOK, query)
}

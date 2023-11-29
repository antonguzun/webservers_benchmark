package api

import (
	"log"
	"net/http"
	"strconv"

	"go_gin/storage"

	"github.com/gin-gonic/gin"
)

func GetUserByIdHandler(c *gin.Context) {
	token := c.GetHeader("token")
	if token != "hardcoded_token" {
		c.String(403, "Forbidden")
		return
	}

	user_id, err := strconv.Atoi(c.Param("user_id"))
	if err != nil {
		c.String(404, "User Not Found")
		return
	}

	repo := c.MustGet("databaseConn").(storage.UserRepo)
	user, err := repo.GetUserById(user_id)
	if err != nil {
		log.Println("get user error", err)
		c.String(500, "Internal Server Error")
		return
	}

	c.JSON(http.StatusOK, user)
}

func UpdateUserHandler(c *gin.Context) {
	token := c.GetHeader("token")
	if token != "hardcoded_token" {
		c.String(403, "Forbidden")
		return
	}

	user_id, err := strconv.Atoi(c.Param("user_id"))
	if err != nil {
		c.String(404, "User Not Found")
		return
	}

	var userUpdate storage.UserUpdate

	if err := c.ShouldBindJSON(&userUpdate); err != nil {
		log.Println("decode get update_data json req err", err)
		c.String(400, "Bad Request")
		return
	}

	repo := c.MustGet("databaseConn").(storage.UserRepo)

	user, err := repo.UpdateUser(user_id, userUpdate)
	if err != nil {
		log.Println("get user error", err)
		c.String(500, "Internal Server Error")
		return
	}

	c.JSON(http.StatusOK, user)
}

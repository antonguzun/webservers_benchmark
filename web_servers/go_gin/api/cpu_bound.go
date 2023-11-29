package api

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

type Query struct {
	Param1 string `json:"param1"`
	Param2 string `json:"param2"`
	Param3 string `json:"param3"`
}

func PlainHandler(c *gin.Context) {
	token := c.GetHeader("token")
	if token != "hardcoded_token" {
		c.String(403, "Forbidden")
		return
	}

	var query Query
	if c.ShouldBind(&query) != nil {
		c.String(400, "Bad Request")
		return
	}

	res := fmt.Sprintf("param1=%s, param2=%s, param3=%s", query.Param1, query.Param2, query.Param3)
	c.String(http.StatusOK, res)
}

func ToJsonHandler(c *gin.Context) {
	token := c.GetHeader("token")
	if token != "hardcoded_token" {
		c.String(403, "Forbidden")
		return
	}

	var query Query
	if c.ShouldBind(&query) != nil {
		c.String(400, "Bad Request")
		return
	}

	c.JSON(http.StatusOK, query)
}

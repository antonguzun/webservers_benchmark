package utils

import (
	"encoding/json"
	"fmt"
	"strconv"

	"github.com/valyala/fasthttp"
)

func DumpData(c *fasthttp.RequestCtx, data interface{}) {
	jsonData, err := json.Marshal(data)
	if err != nil {
		c.Error("Error encoding JSON", fasthttp.StatusInternalServerError)
		return
	}

	c.SetContentType("application/json")
	c.Response.SetStatusCode(fasthttp.StatusOK)
	c.Write(jsonData)
}

func ParseUserID(c *fasthttp.RequestCtx) (int, error) {
	user_id_raw := c.UserValue("user_id")
	user_id, err := strconv.Atoi(fmt.Sprintf("%v", user_id_raw))
	if err != nil {
		return 0, err
	}
	return user_id, nil
}

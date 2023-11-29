package api

import (
	"fmt"

	"go_fasthttp/api/utils"

	"github.com/valyala/fasthttp"
)

type Query struct {
	Param1 string `json:"param1"`
	Param2 string `json:"param2"`
	Param3 string `json:"param3"`
}

func parseParams(c *fasthttp.RequestCtx) Query {
	params := c.QueryArgs()
	param1 := params.Peek("param1")
	param2 := params.Peek("param2")
	param3 := params.Peek("param3")

	return Query{string(param1), string(param2), string(param3)}
}

func PlainHandler(c *fasthttp.RequestCtx) {
	query := parseParams(c)

	res := fmt.Sprintf("param1=%s, param2=%s, param3=%s", query.Param1, query.Param2, query.Param3)
	c.SetBodyString(res)
}

func ToJsonHandler(c *fasthttp.RequestCtx) {
	query := parseParams(c)

	utils.DumpData(c, query)
}

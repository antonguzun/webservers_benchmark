package api

import "github.com/valyala/fasthttp"

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

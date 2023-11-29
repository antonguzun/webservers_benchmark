package api

import (
	"encoding/json"
	"log"

	"go_fasthttp/api/utils"
	"go_fasthttp/storage"

	"github.com/valyala/fasthttp"
)

type Handler struct {
	repo storage.UserRepo
}

func NewHandler(userRepo storage.UserRepo) *Handler {
	return &Handler{repo: userRepo}
}

func (h *Handler) GetUserHandler(c *fasthttp.RequestCtx) {
	user_id, err := utils.ParseUserID(c)
	if err != nil {
		c.Error("User Not Found", 404)
		return
	}

	user, err := h.repo.GetUserById(*user_id)
	if err != nil {
		log.Println("get user error", err)
		c.Error("Internal Server Error", fasthttp.StatusInternalServerError)
		return
	}

	utils.DumpData(c, user)
}

func (h *Handler) UpdateUserHandler(c *fasthttp.RequestCtx) {
	user_id, err := utils.ParseUserID(c)
	if err != nil {
		c.Error("User Not Found", 404)
		return
	}

	var userUpdate storage.UserUpdate
	if err := json.Unmarshal(c.PostBody(), &userUpdate); err != nil {
		log.Println("decode get update_data json req err", err)
		c.Error("Bad Request", 400)
		return
	}

	user, err := h.repo.UpdateUser(*user_id, userUpdate)

	if err != nil {
		log.Println(err)
		log.Println("update user error", err)
		c.Error("Internal Server Error", fasthttp.StatusInternalServerError)
		return
	}
	utils.DumpData(c, user)
}

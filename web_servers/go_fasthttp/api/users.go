package api

import (
	"encoding/json"
	"log"

	"go_fasthttp/api/utils"
	"go_fasthttp/storage"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/valyala/fasthttp"
)

type Handler struct {
	DB *pgxpool.Pool
}

func NewHandler(db *pgxpool.Pool) *Handler {
	return &Handler{DB: db}
}

func (h *Handler) GetUserHandler(c *fasthttp.RequestCtx) {
	user_id, err := utils.ParseUserID(c)
	if err != nil {
		c.Error("User Not Found", 404)
		return
	}

	user, err := storage.GetUserById(h.DB, user_id)
	if err != nil {
		log.Println(err)
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
	if userUpdate.Username == "" || userUpdate.Email == "" {
		log.Println("username:", userUpdate.Username)
		log.Println("email:", userUpdate.Email)
		c.Error("Bad Request", 400)
		return
	}

	user, err := storage.UpdateUser(h.DB, user_id, userUpdate)

	if err != nil {
		log.Println(err)
		c.Error("Internal Server Error", fasthttp.StatusInternalServerError)
		return
	}
	utils.DumpData(c, user)
}

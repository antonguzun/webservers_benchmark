request = function()
    wrk.headers["Connection"] = "Keep-Alive"
    user_id = math.random(1,10000)
    path = "/user/" .. user_id .. "/"
    return wrk.format("GET", path)
  end
request = function()
  wrk.headers["Connection"] = "Keep-Alive"
  wrk.headers["token"] = "hardcoded_token"
  user_id = math.random(1, 10000)
  path = "/user/" .. user_id .. "/"
  return wrk.format("GET", path)
end

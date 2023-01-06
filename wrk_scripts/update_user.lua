function RandomVariable(length)
    local res = ""
    for i = 1, length do
        res = res .. string.char(math.random(97, 122))
    end
    return res
end

request = function()
    wrk.headers["Connection"] = "Keep-Alive"
    wrk.headers["token"] = "hardcoded_token"
    user_id = math.random(1, 10000)
    path = "/user/" .. user_id .. "/"
    local username = RandomVariable(24)
    local email = RandomVariable(24) .. "@gmail.com"
    wrk.body = "{\"username\": \"" .. username .. "\", \"email\": \"" .. email .. "\"}"
    return wrk.format("PATCH", path)
end

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
    param1 = RandomVariable(math.random(14, 14 + 25))
    param2 = RandomVariable(math.random(14, 14 + 25))
    param3 = RandomVariable(math.random(14, 14 + 25))
    param4 = RandomVariable(math.random(14, 14 + 25))

    path = "/plain/?param1=" .. param1 .. "&param2=" .. param2 .. "&param3=" .. param3 .. "&param4=" .. param4
    return wrk.format("GET", path)
end

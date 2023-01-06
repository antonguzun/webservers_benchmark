each web server should contain:
- logging
- sentry integration
- input and output validation



# run bench
## run deps
```sh
docker-coompose up -d
```



```
wrk -t2 -c100 -d30s --latency -s ./wrk_scripts/get_user_by_pk.lua http://127.0.0.1:8000/
```

```
wrk -t2 -c100 -d30s --latency -s ./wrk_scripts/update_user.lua http://127.0.0.1:8000/
```

```
curl -XPATCH 'localhost:8000/user/5/' --header 'token: hardcoded_token' -d '{"username":"asdsfafaf", "email": "asdsagagwe324@gmail.com"}' --header 'Content-Type: application/json'
```

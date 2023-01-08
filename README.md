# webservers_benchmark


## Results
| test_name   | webserver_name | database | orm   | requests_per_second | latency_p50 | latency_p75 | latency_p90 | latency_p99 |
|-------------|----------------|----------|-------|---------------------|-------------|-------------|-------------|-------------|
| get user    | fastapi        | postgres | false | 5538.47             | 22.91ms     | 40.73ms     | 44.75ms     | 52.73ms     |
| get user    | fastapi        | postgres | true  | 2255.56             | 46.06ms     | 75.95ms     | 134.21ms    | 311.16ms    |
| get user    | fastapi        | mysql    | false | 5399.62             | 22.72ms     | 41.15ms     | 44.26ms     | 57.89ms     |
| get user    | fastapi        | mysql    | true  | 2944.57             | 31.78ms     | 52.65ms     | 66.46ms     | 98.85ms     |
| update user | fastapi        | postgres | false | 3898.17             | 24.21ms     | 45.42ms     | 52.64ms     | 72.94ms     |
| update user | fastapi        | postgres | true  | 1276.7              | 74.15ms     | 98.59ms     | 150.44ms    | 248.76ms    |
| update user | fastapi        | mysql    | false | 2949.96             | 34.91ms     | 52.83ms     | 74.37ms     | 451.15ms    |
| update user | fastapi        | mysql    | true  | 1819.76             | 52.75ms     | 76.96ms     | 96.12ms     | 172.90ms    |
| to json     | fastapi        | - | - | 7722.41             | 15.52ms     | 29.14ms     | 41.76ms     | 43.45ms     |
| plain       | fastapi        | - | - | 7716.73             | 15.50ms     | 29.15ms     | 41.76ms     | 43.50ms     |


## run bench
- install python3.11
- install wrk
- install docker-compose
- mariadb driver for mysql testcases
- run deps
```
docker-compose up -d
```
- install local venv
```
python3.11 -m venv venv
```
- install reqs
```
pip install -r requirements.txt
```
- run bench
```
python run_bench.py
```


## debug commands
```
wrk -t2 -c100 -d30s --latency -s ./wrk_scripts/get_user_by_pk.lua http://127.0.0.1:8000/
```

```
wrk -t2 -c100 -d30s --latency -s ./wrk_scripts/update_user.lua http://127.0.0.1:8000/
```

```
curl -XGET 'localhost:8000/user/5/' --header 'token: hardcoded_token'
```

```
curl -XPATCH 'localhost:8000/user/5/' --header 'token: hardcoded_token' -d '{"username":"asdsfafaf", "email": "asdsagagwe324@gmail.com"}' --header 'Content-Type: application/json'
```

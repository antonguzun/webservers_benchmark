# webservers_benchmark

1. [Resources](#Resources)
2. [Methodology](#Methodology)
3. [Tests](#Tests)
4. [Results](#Results)
5. [Run](#Run)
6. [Debug](#Debug)

# Resources

AMD Ryzen 7 PRO 5750G with Radeon Graphics

Fedora Linux 35

Python3.11 for python webservers

# Methodology

Each webserver run in 8 threads or processes

Produce requests for random object with random params

The database contains 10000 rows of objects with random values

Restore the database before each running webserver

# Tests

`get user` is test which produce:

- deserialization path and headers
- comparison token header
- single select query by indexed pk to db
- deserialization row into object/structure
- serialization into json

`update user` is test which produce:

- deserialization path, headers and body
- comparison token header
- single update query by indexed pk to db
- query new state of object
- deserialization row into object/structure
- serialization into json

`plain` is test which produce:

- deserialization path, headers
- comparison token header
- serialization params into string

`to json` is test which produce:

- deserialization path, headers
- comparison token header
- serialization params into json

# Results
## single query, select by pk

|test_name|webserver_name|database| orm |req/sec|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|--------------|--------|-----|-------------------|-----------|-----------|-----------|-----------|
| get user|     sanic    |postgres|False|      19718.93     |   4.55ms  |   5.78ms  |  10.75ms  |  17.66ms  |
| get user|     sanic    |  mysql |False|      17552.93     |   5.76ms  |   7.38ms  |   8.06ms  |   9.62ms  |
| get user|    aiohttp   |postgres|False|      16675.81     |   5.11ms  |   7.66ms  |  14.33ms  |  34.39ms  |
| get user|    aiohttp   |  mysql |False|      15238.32     |   5.76ms  |   8.63ms  |  13.52ms  |  14.72ms  |
| get user|    fastapi   |  mysql |False|      10628.6      |   9.17ms  |  12.57ms  |  17.26ms  |  19.68ms  |
| get user|    fastapi   |postgres|False|      10162.85     |   8.77ms  |  14.71ms  |  27.65ms  |  61.53ms  |
| get user|    aiohttp   |postgres| True|      5252.83      |  12.65ms  |  31.46ms  |  48.86ms  |  151.48ms |
| get user|     sanic    |  mysql | True|      4962.36      |  17.57ms  |  27.00ms  |  35.23ms  |  51.25ms  |
| get user|    aiohttp   |  mysql | True|      4653.78      |  21.64ms  |  35.78ms  |  40.35ms  |  52.91ms  |
| get user|     sanic    |postgres| True|      3956.58      |  19.77ms  |  42.88ms  |  76.93ms  |  190.46ms |
| get user|    fastapi   |  mysql | True|      3910.85      |  20.22ms  |  42.55ms  |  66.47ms  |  118.68ms |
| get user|    fastapi   |postgres| True|      3896.73      |  21.76ms  |  41.49ms  |  68.02ms  |  178.77ms |
| get user|  django_asgi |postgres| True|       875.28      |  103.43ms |  146.67ms |  184.53ms |  262.59ms |

## update query by pk with returning

| test_name |webserver_name|database| orm |req/sec|latency_p50|latency_p75|latency_p90|latency_p99|
|-----------|--------------|--------|-----|-------------------|-----------|-----------|-----------|-----------|
|update user|    aiohttp   |postgres|False|      12691.72     |   7.56ms  |   9.24ms  |  10.65ms  |  13.89ms  |
|update user|     sanic    |postgres|False|      11558.09     |   7.91ms  |  10.16ms  |  21.08ms  |  42.14ms  |
|update user|     sanic    |  mysql |False|      7844.53      |  11.74ms  |  16.54ms  |  22.90ms  |  40.31ms  |
|update user|    fastapi   |postgres|False|      7108.98      |  12.76ms  |  19.10ms  |  26.61ms  |  50.64ms  |
|update user|    aiohttp   |  mysql |False|      5403.76      |  16.51ms  |  24.82ms  |  35.83ms  |  87.23ms  |
|update user|    fastapi   |  mysql |False|      5053.28      |  17.62ms  |  25.54ms  |  36.60ms  |  69.04ms  |
|update user|     sanic    |postgres| True|      3246.06      |  31.89ms  |  43.43ms  |  70.51ms  |  177.10ms |
|update user|    aiohttp   |  mysql | True|      3079.27      |  32.92ms  |  43.83ms  |  50.90ms  |  71.36ms  |
|update user|    aiohttp   |postgres| True|      3053.93      |  29.37ms  |  49.17ms  |  84.96ms  |  208.10ms |
|update user|     sanic    |  mysql | True|      2625.22      |  38.50ms  |  45.98ms  |  53.13ms  |  502.15ms |
|update user|    fastapi   |  mysql | True|      2497.89      |  27.22ms  |  61.75ms  |  93.15ms  |  177.00ms |
|update user|    fastapi   |postgres| True|      2182.01      |  42.59ms  |  56.48ms  |  78.46ms  |  157.21ms |

## plain text with reading header and query params

|test_name|webserver_name|database| orm|req/sec|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|--------------|--------|----|-------------------|-----------|-----------|-----------|-----------|
|  plain  |     sanic    |  None  |None|      69700.5      |   1.18ms  |   2.18ms  |   2.53ms  |   4.49ms  |
|  plain  |    aiohttp   |  None  |None|      41540.48     |   2.49ms  |   3.97ms  |   5.33ms  |   7.66ms  |
|  plain  |    fastapi   |  None  |None|      18465.76     |   5.59ms  |   9.08ms  |  13.35ms  |  19.84ms  |
|  plain  |  django_asgi |  None  |None|      2681.32      |  30.53ms  |  47.30ms  |  58.13ms  |  91.46ms  |

## json serialization with reading header and query params

|test_name|webserver_name|database| orm|req/sec|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|--------------|--------|----|-------------------|-----------|-----------|-----------|-----------|
| to json |     sanic    |  None  |None|      66559.11     |   1.17ms  |   2.10ms  |   2.43ms  |   3.93ms  |
| to json |    aiohttp   |  None  |None|      45675.28     |   1.76ms  |   2.65ms  |   4.22ms  |   6.30ms  |
| to json |    fastapi   |  None  |None|      20996.95     |   4.56ms  |   6.08ms  |   9.03ms  |  12.88ms  |
| to json |  django_asgi |  None  |None|      2192.78      |  46.00ms  |  63.93ms  |  93.15ms  |  137.00ms |

# Run

- install python3.11
- install wrk
- install docker-compose
- mariadb driver for mysql testcases (mariadb-devel)
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
- dump results to markdown tables 
```
python create_markdown_tables.py
```

# Debug

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

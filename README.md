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

`get user` is a test which produces:

- deserialization path and headers
- comparison token header
- single select query by indexed pk to db
- deserialization row into object/structure
- serialization into json

`update user` is a test which produces:

- deserialization path, headers and body
- comparison token header
- single update query by indexed pk to db
- query new state of object
- deserialization row into object/structure
- serialization into json

`plain` is a test which produces:

- deserialization path, headers
- comparison token header
- serialization params into string

`to json` is a test which produces:

- deserialization path, headers
- comparison token header
- serialization params into json

# Results

## single query, select by pk

|test_name|  webserver_name |database| orm |requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|-----------------|--------|-----|-------------------|-----------|-----------|-----------|-----------|
| get user|    actix-web    |postgres|False|      51206.91     |   1.87ms  |   2.21ms  |   2.56ms  |   3.31ms  |
| get user|      sanic      |postgres|False|      18444.9      |   5.24ms  |   6.55ms  |   9.76ms  |  17.42ms  |
| get user|      sanic      |  mysql |False|      17362.0      |   5.28ms  |   6.91ms  |  12.42ms  |  15.90ms  |
| get user|aiohttp[gunicorn]|postgres|False|      15801.49     |   6.72ms  |   7.73ms  |   8.66ms  |  12.39ms  |
| get user|aiohttp[gunicorn]|  mysql |False|      14511.92     |   6.49ms  |  11.25ms  |  14.44ms  |  19.59ms  |
| get user| fastapi[uvicorn]|  mysql |False|      10597.79     |   5.07ms  |  16.98ms  |  32.43ms  |  44.55ms  |
| get user| fastapi[uvicorn]|postgres|False|      10496.37     |   9.08ms  |  13.66ms  |  19.01ms  |  37.37ms  |
| get user|      sanic      |postgres| True|      4976.13      |  16.40ms  |  37.74ms  |  59.00ms  |  168.36ms |
| get user|      sanic      |  mysql | True|      4640.02      |  20.13ms  |  26.16ms  |  38.89ms  |  50.82ms  |
| get user|aiohttp[gunicorn]|  mysql | True|      4628.34      |  18.55ms  |  28.75ms  |  43.32ms  |  72.57ms  |
| get user|aiohttp[gunicorn]|postgres| True|      4465.36      |  18.66ms  |  32.90ms  |  51.64ms  |  142.45ms |
| get user| fastapi[uvicorn]|postgres| True|      4022.73      |  25.58ms  |  46.62ms  |  67.47ms  |  172.25ms |
| get user| fastapi[uvicorn]|  mysql | True|      3720.82      |  20.51ms  |  39.27ms  |  70.76ms  |  125.79ms |

## update query by pk with returning

| test_name |  webserver_name |database| orm |requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|-----------|-----------------|--------|-----|-------------------|-----------|-----------|-----------|-----------|
|update user|    actix-web    |postgres|False|      15146.64     |   5.75ms  |   7.72ms  |  13.49ms  |  35.39ms  |
|update user|      sanic      |postgres|False|      9977.64      |   9.27ms  |  12.16ms  |  19.61ms  |  45.51ms  |
|update user|aiohttp[gunicorn]|postgres|False|      8689.96      |   8.74ms  |  16.57ms  |  24.87ms  |  145.77ms |
|update user| fastapi[uvicorn]|postgres|False|      6290.28      |  14.55ms  |  19.67ms  |  26.45ms  |  44.63ms  |
|update user|      sanic      |  mysql |False|      3996.28      |  21.68ms  |  33.60ms  |  48.11ms  |  100.03ms |
|update user|aiohttp[gunicorn]|  mysql |False|      3692.28      |  24.42ms  |  34.67ms  |  54.42ms  |  135.78ms |
|update user| fastapi[uvicorn]|  mysql |False|      3390.27      |  26.76ms  |  37.53ms  |  61.43ms  |  147.49ms |
|update user|      sanic      |postgres| True|      2616.28      |  33.59ms  |  50.20ms  |  86.53ms  |  289.58ms |
|update user|aiohttp[gunicorn]|  mysql | True|      2597.68      |  33.53ms  |  52.55ms  |  67.93ms  |  137.67ms |
|update user|aiohttp[gunicorn]|postgres| True|      2426.91      |  39.41ms  |  64.36ms  |  109.40ms |  215.98ms |
|update user|      sanic      |  mysql | True|      2252.01      |  41.49ms  |  60.61ms  |  75.45ms  |  117.92ms |
|update user| fastapi[uvicorn]|  mysql | True|      2046.17      |  45.50ms  |  60.54ms  |  78.81ms  |  263.17ms |
|update user| fastapi[uvicorn]|postgres| True|      1667.16      |  50.38ms  |  73.36ms  |  112.73ms |  200.01ms |

## plain text with reading header and query params

|test_name|  webserver_name |database| orm|requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|-----------------|--------|----|-------------------|-----------|-----------|-----------|-----------|
|  plain  |      hyper      |  None  |None|     122684.73     |  398.00us |  547.00us |  698.00us |   0.92ms  |
|  plain  |    actix-web    |  None  |None|     120822.14     |  402.00us |  519.00us |  681.00us |   0.90ms  |
|  plain  |      sanic      |  None  |None|      62475.41     |   1.72ms  |   2.28ms  |   3.10ms  |   5.10ms  |
|  plain  |aiohttp[gunicorn]|  None  |None|      42771.58     |   1.72ms  |   4.25ms  |   5.99ms  |   8.88ms  |
|  plain  |   hyper[sync]   |  None  |None|      27611.18     |  22.00us  |  31.00us  |  32.00us  |  38.00us  |
|  plain  | fastapi[uvicorn]|  None  |None|      22601.78     |   5.12ms  |   6.44ms  |   8.07ms  |  11.80ms  |
|  plain  |      django     |  None  |None|      11786.33     |   8.31ms  |   8.49ms  |   8.69ms  |   9.15ms  |
|  plain  |   django_asgi   |  None  |None|      2050.62      |  47.17ms  |  64.42ms  |  80.98ms  |  122.38ms |

## json serialization with reading header and query params

|test_name|  webserver_name |database| orm|requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|-----------------|--------|----|-------------------|-----------|-----------|-----------|-----------|
| to json |      hyper      |  None  |None|     123304.23     |  398.00us |  557.00us |  699.00us |   0.92ms  |
| to json |    actix-web    |  None  |None|     120712.25     |  401.00us |  514.00us |  681.00us |   0.90ms  |
| to json |      sanic      |  None  |None|      65164.48     |   1.47ms  |   1.79ms  |   2.07ms  |   3.07ms  |
| to json |aiohttp[gunicorn]|  None  |None|      45527.54     |   1.94ms  |   2.81ms  |   3.22ms  |   4.78ms  |
| to json |   hyper[sync]   |  None  |None|      26695.98     |  23.00us  |  31.00us  |  32.00us  |  39.00us  |
| to json | fastapi[uvicorn]|  None  |None|      23306.94     |   4.53ms  |   6.01ms  |   8.59ms  |  12.20ms  |
| to json |      django     |  None  |None|      11382.3      |   8.40ms  |   8.59ms  |   8.82ms  |  852.48ms |
| to json |   django_asgi   |  None  |None|      2251.88      |  45.41ms  |  61.54ms  |  90.64ms  |  115.91ms |

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

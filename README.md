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

|test_name|  webserver_name |database| orm |req/sec|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|-----------------|--------|-----|-------------------|-----------|-----------|-----------|-----------|
| get user|    actix-web    |postgres|False|      42695.91     |   2.23ms  |   2.67ms  |   3.14ms  |   4.17ms  |
| get user|      sanic      |postgres|False|      17017.3      |   5.60ms  |   6.90ms  |   8.64ms  |  13.60ms  |
| get user|      sanic      |  mysql |False|      15404.85     |   6.00ms  |   7.96ms  |  13.11ms  |  16.56ms  |
| get user|aiohttp[gunicorn]|postgres|False|      13808.83     |   7.70ms  |   8.86ms  |  11.52ms  |  21.53ms  |
| get user|aiohttp[gunicorn]|  mysql |False|      13070.92     |   6.13ms  |   9.45ms  |  14.93ms  |  16.76ms  |
| get user| fastapi[uvicorn]|  mysql |False|       9330.6      |  10.21ms  |  13.81ms  |  18.81ms  |  21.99ms  |
| get user| fastapi[uvicorn]|postgres|False|      9300.22      |  11.01ms  |  13.26ms  |  17.12ms  |  37.82ms  |
| get user|aiohttp[gunicorn]|  mysql | True|      3796.48      |  24.79ms  |  38.93ms  |  51.32ms  |  89.35ms  |
| get user|      sanic      |  mysql | True|      3722.48      |  22.77ms  |  31.82ms  |  51.32ms  |  69.62ms  |
| get user|aiohttp[gunicorn]|postgres| True|      3547.97      |  19.34ms  |  43.92ms  |  79.25ms  |  202.06ms |
| get user|      sanic      |postgres| True|      3532.72      |  24.24ms  |  42.59ms  |  73.48ms  |  221.97ms |
| get user| fastapi[uvicorn]|  mysql | True|      3122.42      |  28.18ms  |  44.45ms  |  72.92ms  |  115.46ms |
| get user| fastapi[uvicorn]|postgres| True|       2795.5      |  31.11ms  |  49.16ms  |  81.45ms  |  209.01ms |
| get user|      django     |postgres| True|       745.29      |  113.03ms |  167.51ms |  180.18ms |  193.60ms |
| get user|   django_asgi   |postgres| True|       616.12      |  130.52ms |  216.86ms |  315.62ms |  463.75ms |

## update query by pk with returning

| test_name |  webserver_name |database| orm |req/sec|latency_p50|latency_p75|latency_p90|latency_p99|
|-----------|-----------------|--------|-----|-------------------|-----------|-----------|-----------|-----------|
|update user|    actix-web    |postgres|False|      16659.24     |   5.46ms  |   7.05ms  |   8.86ms  |  19.13ms  |
|update user|      sanic      |postgres|False|      10574.87     |   8.96ms  |  11.17ms  |  13.38ms  |  18.97ms  |
|update user|aiohttp[gunicorn]|postgres|False|      7456.68      |  12.85ms  |  18.42ms  |  23.44ms  |  36.48ms  |
|update user| fastapi[uvicorn]|postgres|False|      6112.13      |  15.29ms  |  24.06ms  |  30.86ms  |  61.79ms  |
|update user|      sanic      |  mysql |False|      5016.44      |  17.84ms  |  23.64ms  |  33.44ms  |  77.05ms  |
|update user|aiohttp[gunicorn]|  mysql |False|      4088.09      |  21.57ms  |  30.32ms  |  42.54ms  |  527.23ms |
|update user| fastapi[uvicorn]|  mysql |False|      3660.46      |  24.70ms  |  33.48ms  |  45.65ms  |  89.82ms  |
|update user|aiohttp[gunicorn]|  mysql | True|      2299.73      |  39.38ms  |  56.77ms  |  71.60ms  |  103.33ms |
|update user|      sanic      |  mysql | True|      2243.87      |  43.87ms  |  60.26ms  |  73.81ms  |  111.10ms |
|update user| fastapi[uvicorn]|  mysql | True|      1915.04      |  49.00ms  |  71.02ms  |  89.06ms  |  496.85ms |
|update user| fastapi[uvicorn]|postgres| True|       1903.7      |  52.91ms  |  68.11ms  |  96.91ms  |  194.88ms |
|update user|      sanic      |postgres| True|      1846.27      |  46.40ms  |  67.18ms  |  98.79ms  |  205.93ms |
|update user|aiohttp[gunicorn]|postgres| True|      1791.98      |  49.38ms  |  65.97ms  |  100.60ms |  309.37ms |

## plain text with reading header and query params

|test_name|  webserver_name |database| orm|req/sec|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|-----------------|--------|----|-------------------|-----------|-----------|-----------|-----------|
|  plain  |    actix-web    |  None  |None|     115057.17     |  425.00us |  556.00us |  740.00us |   0.95ms  |
|  plain  |      sanic      |  None  |None|      59841.8      |   1.64ms  |   2.30ms  |   2.91ms  |   4.56ms  |
|  plain  |aiohttp[gunicorn]|  None  |None|      40381.7      |   2.06ms  |   3.69ms  |   5.74ms  |   6.90ms  |
|  plain  | fastapi[uvicorn]|  None  |None|      20734.05     |   3.88ms  |   8.65ms  |  12.87ms  |  20.62ms  |
|  plain  |      django     |  None  |None|      11371.27     |   8.60ms  |   8.78ms  |   9.01ms  |   9.71ms  |
|  plain  |   django_asgi   |  None  |None|      2168.31      |  48.40ms  |  77.84ms  |  109.43ms |  151.87ms |

## json serialization with reading header and query params

|test_name|  webserver_name |database| orm|req/sec|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|-----------------|--------|----|-------------------|-----------|-----------|-----------|-----------|
| to json |    actix-web    |  None  |None|     114692.94     |  422.00us |  543.00us |  738.00us |   0.95ms  |
| to json |      sanic      |  None  |None|      65103.3      |   1.24ms  |   1.75ms  |   2.49ms  |   4.39ms  |
| to json |aiohttp[gunicorn]|  None  |None|      42652.95     |   2.26ms  |   3.17ms  |   3.94ms  |   5.42ms  |
| to json | fastapi[uvicorn]|  None  |None|      22756.52     |   3.77ms  |   5.64ms  |   8.12ms  |  12.49ms  |
| to json |      django     |  None  |None|      11000.97     |   8.76ms  |   8.97ms  |   9.22ms  |  203.64ms |
| to json |   django_asgi   |  None  |None|      1691.61      |  72.35ms  |  116.38ms |  171.92ms |  241.95ms |

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

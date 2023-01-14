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

Python3.11 (cpython interpreter) for python webservers

rustc 1.65.0 (897e37553 2022-11-02) for rust webservers


# Methodology

Each webserver run in single thread and single process.
That makes easier maintenance, log/metrics collection, resources manipulation.
I guess the optimal scenario is using external load balancer as nginx/istio/ingress.
Ofc if you are using python with wsgi/asgi webservers you could get better measurements without extra infrastructure.

Produce requests for random object with random params

The database contains 10000 rows of objects with random values

Restore the database before each running webserver

# Tests

`get user` is a test which do:

- deserialization path and headers
- comparison token header
- single select query by indexed pk to db
- deserialization row into object/structure
- serialization into json

`update user` is a test which do:

- deserialization path, headers and body
- comparison token header
- single update query by indexed pk to db
- query new state of object
- deserialization row into object/structure
- serialization into json

`plain` is a test which do:

- deserialization path, headers
- comparison token header
- serialization params into string

`to json` is a test which do:

- deserialization path, headers
- comparison token header
- serialization params into json

# Results

## single query, select by pk

|language|  webserver_name |database|      orm     |requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|--------|-----------------|--------|--------------|-------------------|-----------|-----------|-----------|-----------|
|  rust  |    actix-web    |postgres|     None     |      20453.14     |   4.77ms  |   5.15ms  |   5.40ms  |  62.26ms  |
|  rust  |       axum      |postgres|     None     |      19990.2      |   4.73ms  |   5.59ms  |   6.29ms  |  74.62ms  |
| python |      sanic      |postgres|     None     |      5210.99      |  18.92ms  |  19.47ms  |  20.27ms  |  37.29ms  |
| python |      sanic      |  mysql |     None     |      3708.09      |  26.12ms  |  26.74ms  |  27.44ms  |  47.20ms  |
| python |aiohttp[gunicorn]|postgres|     None     |      3008.69      |  32.31ms  |  60.09ms  |  111.95ms |  199.07ms |
| python |aiohttp[gunicorn]|  mysql |     None     |      2438.46      |  39.46ms  |  40.08ms  |  41.00ms  |  79.76ms  |
| python | fastapi[uvicorn]|postgres|     None     |      1850.22      |  51.37ms  |  52.94ms  |  81.03ms  |  98.14ms  |
| python | fastapi[uvicorn]|  mysql |     None     |      1712.94      |  55.80ms  |  56.46ms  |  57.25ms  |  112.29ms |
| python |      sanic      |postgres|SQLAlchemy ORM|      1442.47      |  62.12ms  |  132.45ms |  212.24ms |  442.86ms |
| python |      sanic      |  mysql |SQLAlchemy ORM|      1422.95      |  68.07ms  |  73.53ms  |  124.39ms |  239.81ms |
| python |aiohttp[gunicorn]|postgres|SQLAlchemy ORM|      1117.98      |  20.69ms  |  216.82ms |  358.09ms |  639.04ms |
| python |aiohttp[gunicorn]|  mysql |SQLAlchemy ORM|       979.59      |  96.31ms  |  165.90ms |  243.65ms |  375.81ms |
| python | fastapi[uvicorn]|postgres|SQLAlchemy ORM|       838.15      |  28.76ms  |  297.57ms |  614.05ms |   1.13s   |
| python | fastapi[uvicorn]|  mysql |SQLAlchemy ORM|       782.94      |  120.97ms |  181.37ms |  281.39ms |  476.66ms |
| python |   django_asgi   |postgres|  Django ORM  |       310.18      |  292.19ms |  340.35ms |  371.40ms |  438.06ms |
| python |      django     |postgres|  Django ORM  |       163.29      |  597.54ms |  607.57ms |  611.25ms |  631.23ms |

## update query by pk with returning

|language|  webserver_name |database|      orm     |requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|--------|-----------------|--------|--------------|-------------------|-----------|-----------|-----------|-----------|
|  rust  |    actix-web    |postgres|     None     |      14981.35     |   6.51ms  |   6.99ms  |   7.56ms  |  10.09ms  |
|  rust  |       axum      |postgres|     None     |      12746.7      |   6.74ms  |   7.91ms  |  12.32ms  |  57.32ms  |
| python |      sanic      |postgres|     None     |       3784.3      |  23.84ms  |  25.01ms  |  43.80ms  |  72.64ms  |
| python |aiohttp[gunicorn]|postgres|     None     |      2528.21      |  38.72ms  |  39.62ms  |  40.82ms  |  73.24ms  |
| python |      sanic      |  mysql |     None     |       1847.2      |  37.24ms  |  88.51ms  |  138.16ms |  233.31ms |
| python | fastapi[uvicorn]|postgres|     None     |      1479.28      |  63.78ms  |  65.81ms  |  88.45ms  |  120.08ms |
| python |aiohttp[gunicorn]|  mysql |     None     |      1383.66      |  55.94ms  |  99.25ms  |  144.84ms |  194.30ms |
| python | fastapi[uvicorn]|  mysql |     None     |      1152.36      |  76.95ms  |  114.66ms |  155.72ms |  255.67ms |
| python |      sanic      |postgres|SQLAlchemy ORM|       958.0       |  91.18ms  |  164.75ms |  300.19ms |  554.97ms |
| python |      sanic      |  mysql |SQLAlchemy ORM|       944.39      |  101.73ms |  172.74ms |  249.61ms |  435.29ms |
| python |aiohttp[gunicorn]|postgres|SQLAlchemy ORM|       743.91      |  116.11ms |  243.25ms |  393.73ms |  776.92ms |
| python |aiohttp[gunicorn]|  mysql |SQLAlchemy ORM|       638.73      |  141.88ms |  269.23ms |  451.60ms |  977.23ms |
| python | fastapi[uvicorn]|postgres|SQLAlchemy ORM|       607.51      |  146.12ms |  265.35ms |  429.68ms |  892.22ms |
| python | fastapi[uvicorn]|  mysql |SQLAlchemy ORM|       557.2       |  170.34ms |  268.78ms |  388.03ms |  709.95ms |
| python |   django_asgi   |postgres|  Django ORM  |       265.46      |  344.73ms |  358.33ms |  399.86ms |  430.74ms |
| python |      django     |postgres|  Django ORM  |       125.5       |  778.22ms |  785.45ms |  788.39ms |  800.48ms |

## plain text with reading header and query params

|language|  webserver_name |requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|--------|-----------------|-------------------|-----------|-----------|-----------|-----------|
|  rust  |    actix-web    |     133169.06     |  358.00us |  504.00us |  690.00us |   1.30ms  |
|  rust  |       axum      |     131915.03     |  556.00us |  683.00us |  733.00us |   1.12ms  |
|  rust  |      hyper      |     126911.47     |  368.00us |  445.00us |  663.00us |  15.14ms  |
|  rust  |   hyper[sync]   |      25417.01     |  25.00us  |  31.00us  |  32.00us  |  52.00us  |
| python |      sanic      |      23068.33     |   4.18ms  |   4.47ms  |   4.78ms  |   7.78ms  |
| python |aiohttp[gunicorn]|      6875.18      |  15.03ms  |  15.53ms  |  16.05ms  |  19.81ms  |
| python | fastapi[uvicorn]|      3403.86      |  30.49ms  |  32.01ms  |  33.59ms  |  58.24ms  |
| python |      django     |      1772.67      |  55.75ms  |  55.98ms  |  56.25ms  |  66.32ms  |
| python |   django_asgi   |       537.54      |  170.85ms |  189.87ms |  218.62ms |  261.40ms |

## json serialization with reading header and query params

|language|  webserver_name |requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|--------|-----------------|-------------------|-----------|-----------|-----------|-----------|
|  rust  |    actix-web    |     132738.17     |  363.00us |  596.00us |  687.00us |   1.18ms  |
|  rust  |       axum      |     132577.75     |  693.00us |  731.00us |  775.00us |   1.07ms  |
|  rust  |      hyper      |      129449.2     |  363.00us |  468.00us |  679.00us |  28.33ms  |
|  rust  |   hyper[sync]   |      24228.53     |  31.00us  |  32.00us  |  35.00us  |  52.00us  |
| python |      sanic      |      21612.87     |   4.52ms  |   4.79ms  |   5.05ms  |   6.41ms  |
| python |aiohttp[gunicorn]|      6561.11      |  15.60ms  |  16.36ms  |  17.86ms  |  21.59ms  |
| python | fastapi[uvicorn]|      3319.11      |  31.32ms  |  32.99ms  |  34.96ms  |  60.82ms  |
| python |      django     |      1759.76      |  56.15ms  |  56.43ms  |  56.75ms  |  60.71ms  |
| python |   django_asgi   |       497.53      |  183.84ms |  208.93ms |  213.29ms |  229.48ms |

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

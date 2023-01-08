# webservers_benchmark


## Resources:

AMD Ryzen 7 PRO 5750G with Radeon Graphics

Fedora Linux 35

Python3.11 for python webservers

## single query, select by pk

|test_name|webserver_name|database| orm |requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|--------------|--------|-----|-------------------|-----------|-----------|-----------|-----------|
| get user|     sanic    |postgres|False|      16392.63     |   5.68ms  |   7.40ms  |   9.73ms  |  17.00ms  |
| get user|     sanic    |postgres| True|       4044.1      |  20.17ms  |  42.50ms  |  77.06ms  |  222.32ms |
| get user|     sanic    |  mysql |False|      15348.8      |   5.71ms  |   9.01ms  |  10.94ms  |  15.32ms  |
| get user|     sanic    |  mysql | True|      4180.49      |  21.19ms  |  29.87ms  |  42.37ms  |  61.79ms  |
| get user|    fastapi   |postgres|False|      6960.06      |  15.26ms  |  18.99ms  |  24.77ms  |  52.91ms  |
| get user|    fastapi   |postgres| True|      2448.88      |  36.92ms  |  70.81ms  |  114.84ms |  304.38ms |
| get user|    fastapi   |  mysql |False|      5781.06      |  15.10ms  |  25.03ms  |  34.60ms  |  54.72ms  |
| get user|    fastapi   |  mysql | True|      3084.09      |  29.33ms  |  43.37ms  |  71.12ms  |  105.94ms |
| get user|    aiohttp   |postgres|False|      12619.04     |   7.12ms  |  11.93ms  |  18.33ms  |  38.30ms  |
| get user|    aiohttp   |postgres| True|      3615.86      |  21.15ms  |  47.74ms  |  84.12ms  |  265.16ms |
| get user|    aiohttp   |  mysql |False|      12565.67     |   8.56ms  |  10.59ms  |  14.45ms  |  21.41ms  |
| get user|    aiohttp   |  mysql | True|      4186.12      |  19.40ms  |  39.51ms  |  48.70ms  |  76.78ms  |

## update query by pk with returning

| test_name |webserver_name|database| orm |requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|-----------|--------------|--------|-----|-------------------|-----------|-----------|-----------|-----------|
|update user|     sanic    |postgres|False|      10553.61     |   8.47ms  |  11.79ms  |  15.70ms  |  25.56ms  |
|update user|     sanic    |postgres| True|      2581.09      |  42.82ms  |  53.35ms  |  66.71ms  |  146.87ms |
|update user|     sanic    |  mysql |False|      7993.45      |  11.27ms  |  15.85ms  |  22.04ms  |  40.90ms  |
|update user|     sanic    |  mysql | True|      2640.34      |  27.28ms  |  61.55ms  |  87.29ms  |  144.20ms |
|update user|    fastapi   |postgres|False|      5309.65      |  17.53ms  |  24.80ms  |  34.71ms  |  65.73ms  |
|update user|    fastapi   |postgres| True|      1665.46      |  57.55ms  |  78.38ms  |  119.74ms |  287.22ms |
|update user|    fastapi   |  mysql |False|      3261.62      |  27.12ms  |  44.73ms  |  76.51ms  |  155.11ms |
|update user|    fastapi   |  mysql | True|      1926.39      |  43.56ms  |  68.68ms  |  86.18ms  |  131.81ms |
|update user|    aiohttp   |postgres|False|      9129.86      |   9.70ms  |  14.88ms  |  22.64ms  |  41.67ms  |
|update user|    aiohttp   |postgres| True|      1992.86      |  45.99ms  |  76.78ms  |  121.28ms |  265.49ms |
|update user|    aiohttp   |  mysql |False|      6113.24      |  14.74ms  |  20.93ms  |  29.36ms  |  55.67ms  |
|update user|    aiohttp   |  mysql | True|      2603.55      |  32.99ms  |  52.46ms  |  82.21ms  |  184.90ms |

## plain text with reading header and query params

|test_name|webserver_name|database| orm|requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|--------------|--------|----|-------------------|-----------|-----------|-----------|-----------|
|  plain  |     sanic    |  None  |None|      53463.57     |   1.46ms  |   2.50ms  |   3.97ms  |   5.39ms  |
|  plain  |    fastapi   |  None  |None|      12987.79     |   5.82ms  |  12.47ms  |  19.50ms  |  34.74ms  |
|  plain  |    aiohttp   |  None  |None|      35752.39     |   2.84ms  |   4.36ms  |   6.79ms  |  10.80ms  |

## json serialization with reading header and query params

|test_name|webserver_name|database|orm|requests_per_second|latency_p50|latency_p75|latency_p90|latency_p99|
|---------|--------------|--------|---|-------------------|-----------|-----------|-----------|-----------|
| to json |     sanic    |  None  |nan|      53544.9      |   1.78ms  |   2.66ms  |   3.41ms  |   5.37ms  |
| to json |    fastapi   |  None  |nan|      12173.04     |   7.51ms  |  10.66ms  |  15.79ms  |  29.58ms  |
| to json |    aiohttp   |  None  |nan|      35122.02     |   2.71ms  |   4.10ms  |   5.06ms  |   7.54ms  |

## run bench
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

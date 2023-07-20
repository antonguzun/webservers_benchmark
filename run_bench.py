import datetime
import os
import subprocess
import sys
import time
from pathlib import Path

import psutil
import pydantic
import requests
import tomllib
from loguru import logger

web_servers_path = Path("web_servers")
NUMBER_OF_CONCURRENT_CLIENTS = 100
TEST_LENGHT_IN_SEC = 5
WEBSERVER_ADDRES = "http://127.0.0.1:8000/"


def create_wrk_command(script_name: str) -> str:
    return f"wrk -t2 -c{NUMBER_OF_CONCURRENT_CLIENTS} -d{TEST_LENGHT_IN_SEC}s --latency -s ./wrk_scripts/{script_name} {WEBSERVER_ADDRES}"


GET_USER_BENCH = dict(
    name="get user", wrk_command=create_wrk_command(script_name="get_user_by_pk.lua")
)
UPDATE_USER_BENCH = dict(
    name="update user", wrk_command=create_wrk_command(script_name="update_user.lua")
)
PLAIN_TEXT_BENCH = dict(
    name="plain", wrk_command=create_wrk_command(script_name="plain.lua")
)
TO_JSON_BENCH = dict(
    name="to json", wrk_command=create_wrk_command(script_name="to_json.lua")
)
WRK_TESTS = [GET_USER_BENCH, UPDATE_USER_BENCH, TO_JSON_BENCH, PLAIN_TEXT_BENCH]
STATELESS_TEST_NAMES = [TO_JSON_BENCH["name"], PLAIN_TEXT_BENCH["name"]]


class BenchResult(pydantic.BaseModel):
    test_name: str
    webserver_name: str
    language: str
    database: str | None
    orm: str | None

    requests_per_second: float
    latency_p50: str
    latency_p75: str
    latency_p90: str
    latency_p99: str

    @classmethod
    def create_from_wrk_output(
        cls,
        webserver_name: str,
        test_name: str,
        language: str,
        database: str,
        orm: str | None,
        output: str,
    ) -> "BenchResult":
        data = output.splitlines()
        return cls(
            test_name=test_name,
            webserver_name=webserver_name,
            language=language,
            database=database,
            orm=orm,
            requests_per_second=float(data[11].split()[1]),
            latency_p50=data[6].split()[1],
            latency_p75=data[7].split()[1],
            latency_p90=data[8].split()[1],
            latency_p99=data[9].split()[1],
        )


class BenchSummary(pydantic.BaseModel):
    created_at: datetime.date
    results: list[BenchResult]


def log_subprocess_output(pipe, logger):
    logger.info(pipe.splitlines())
    for line in pipe.splitlines():
        logger.info("got line from subprocess: %r", line)
        print("got line from subprocess: %r", line)


def clean_db():
    os.system(
        "psql postgresql://postgres:pass@localhost:15432/webservers_bench < postgres_db.sql"
    )
    os.system(
        "mysql --user=user --password=pass --port=13306 --protocol=tcp webservers_bench < mysql_db.sql"
    )
    os.system("python redis_data_generator.py | redis-cli --pipe -p 26379")
    time.sleep(1)


def database_name(config: dict, test_name: str) -> str:
    if test_name in STATELESS_TEST_NAMES or not config.get("database"):
        return None
    res = config["database"]
    if config.get("db_client"):
        res += f"[{config['db_client']}]"
    return res


def check_service(logger):
    cnt = 300
    start_at = datetime.datetime.now()
    while cnt > 0:
        try:
            ping_res = requests.get("http://localhost:8000/ping/")
            if ping_res.status_code == 200:

                # finish_at = datetime.datetime.now()
                # logger.info(f"Startup time: {(finish_at - start_at).seconds} sec")

                return
        except Exception:
            pass
        time.sleep(0.1)
        cnt -= 1
    finish_at = datetime.datetime.now()
    logger.error(f"Can't start webserver in {(finish_at - start_at).seconds} sec")


if __name__ == "__main__":
    today = datetime.date.today()
    logger.add(
        f"./logs/{today}.log", format="{time:HH:mm:ss} {extra[webserver]} {message}"
    )
    # logger.add(
    #     sys.stdout, format="{time:HH:mm:ss} {extra[webserver]} {message}"
    # )
    root_logger = logger.bind(webserver="root")

    root_logger.info("Running benchmarks")

    finished = set()
    summary = BenchSummary(created_at=datetime.date.today(), results=[])
    errors = []
    for web_server in web_servers_path.iterdir():
        try:
            with open(f"{web_server}/config.toml", "rb") as f:
                config = tomllib.load(f)
            for run_setup_name, run_option in config["run_options"].items():
                webserver_repr = f"{config['name']}-{database_name(run_option, None)}"
                webserver_logger = logger.bind(webserver=webserver_repr)

                if config["language"] != "java":
                    continue
                # if not "sanic" in config["name"]:
                #     continue
                # fast test
                # if len(finished) == 2:
                #     continue
                # if not run_option.get('orm'):
                #     continue

                webserver_logger.debug(
                    f"Running benchmarks for {config['name']} {run_setup_name}"
                )
                webserver_logger.debug(f"Build {config['name']}")
                # output = subprocess.check_output(f"cd {web_server} && {run_option['BUILD_COMMAND']}")
                # webserver_logger.info(output)
                os.system(f"cd {web_server} && {run_option['BUILD_COMMAND']}")
                webserver_logger.debug(
                    f"Start webserver {config['name']} in subprocess"
                )
                webserver_logger.debug("Clean DB")
                clean_db()
                web_server_process = subprocess.Popen(
                    [run_option["RUN_COMMAND"]],
                    shell=True,
                    stdout=subprocess.PIPE,
                )
                webserver_logger.info(f"started {web_server_process.pid}")
                try:
                    for wrk_test in WRK_TESTS:
                        webserver_logger.info(f"check webserver")
                        check_service(webserver_logger)
                        if (
                            wrk_test["name"] in STATELESS_TEST_NAMES
                            and f"{config['name']}_{wrk_test['name']}" in finished
                        ):
                            continue
                        try:
                            webserver_logger.info(f"test {wrk_test['name']}")
                            wrk_process = subprocess.run(
                                wrk_test["wrk_command"],
                                shell=True,
                                stdout=subprocess.PIPE,
                            )
                            # webserver_logger.debug(f"{wrk_test['name']}; result: {wrk_process.stdout}")
                            result = BenchResult.create_from_wrk_output(
                                webserver_name=config["name"],
                                language=config["language"],
                                test_name=wrk_test["name"],
                                database=database_name(run_option, wrk_test["name"]),
                                orm=run_option.get("orm")
                                if wrk_test["name"] not in STATELESS_TEST_NAMES
                                else None,
                                output=wrk_process.stdout,
                            )
                            summary.results.append(result)
                            finished.add(f"{config['name']}_{wrk_test['name']}")
                        except Exception as e:
                            webserver_logger.error(
                                f"Failed to run {wrk_test['name']} test {e}"
                            )
                finally:
                    webserver_logger.error(
                        f"terminate webserver {web_server_process.pid}"
                    )
                    p = psutil.Process(web_server_process.pid)
                    for child in p.children(recursive=True):
                        try:
                            child.kill()
                        except Exception as e:
                            webserver_logger.error(
                                "Failed to kill child process: " + str(e)
                            )
                    p.kill()
                    time.sleep(5)
        except FileNotFoundError:
            root_logger.warning(
                f"Skipping {web_server} as it doesn't have a config.toml file"
            )
            continue

    with open(f"reports/{summary.created_at}.json", "w") as f:
        f.write(summary.json())
    root_logger.info("Done")

import datetime
import os
import subprocess
import time
from pathlib import Path

import psutil
import pydantic
import tomllib
import requests

web_servers_path = Path("web_servers")
NUMBER_OF_CONCURRENT_CLIENTS = 100
TEST_LENGHT_IN_SEC = 5
WEBSERVER_ADDRES = "http://127.0.0.1:8000/"



def create_wrk_command(script_name: str) -> str:
    return f"wrk -t2 -c{NUMBER_OF_CONCURRENT_CLIENTS} -d{TEST_LENGHT_IN_SEC}s --latency -s ./wrk_scripts/{script_name} {WEBSERVER_ADDRES}"


GET_USER_BENCH = dict(name="get user", wrk_command=create_wrk_command(script_name="get_user_by_pk.lua"))
UPDATE_USER_BENCH = dict(name="update user", wrk_command=create_wrk_command(script_name="update_user.lua"))
PLAIN_TEXT_BENCH = dict(name="plain", wrk_command=create_wrk_command(script_name="plain.lua"))
TO_JSON_BENCH = dict(name="to json", wrk_command=create_wrk_command(script_name="to_json.lua"))
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
        cls, webserver_name: str, test_name: str, language:str, database: str, orm: str | None, output: str
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


def clean_db():
    print("Clean DB")
    os.system("psql postgresql://postgres:pass@localhost:15432/webservers_bench < postgres_db.sql")
    os.system("mysql --user=user --password=pass --port=13306 --protocol=tcp webservers_bench < mysql_db.sql")
    os.system("python redis_data_generator.py | redis-cli --pipe -p 26379")
    time.sleep(1)


def database_name(config: dict, test_name: str) -> str:
    if test_name in STATELESS_TEST_NAMES or not config.get("database"):
        return None
    res = config["database"]
    if config.get("db_client"):
        res += f"[{config['db_client']}]"
    return res


def check_service(err):
    cnt = 5
    while cnt > 0:
        try:
            ping_res = requests.get("localhost:8000/ping/")
            if ping_res.status == 200:
                return
        except Exception:
            err.append("Service is not available")
        time.sleep(5)
        cnt -= 1


if __name__ == "__main__":
    print("Running benchmarks")
    finished = set()
    summary = BenchSummary(created_at=datetime.date.today(), results=[])
    errors = []
    for web_server in web_servers_path.iterdir():
        try:
            with open(f"{web_server}/config.toml", "rb") as f:
                config = tomllib.load(f)
            for run_setup_name, run_option in config["run_options"].items():
                # if config['language'] != 'js':
                #     continue
                print(f"Running benchmarks for {config['name']} {run_setup_name}")
                print(f"Build {config['name']}")
                os.system(f"cd {web_server} && {run_option['BUILD_COMMAND']}")
                print(f"Run webserver {config['name']} in subprocess")
                clean_db()
                web_server_process = subprocess.Popen(
                    [run_option["RUN_COMMAND"]],
                    shell=True,
                )
                print(f"started {web_server_process.pid}")
                try:
                    for wrk_test in WRK_TESTS:
                        check_service(errors)
                        if wrk_test['name'] in STATELESS_TEST_NAMES \
                            and f"{config['name']}_{wrk_test['name']}" in finished:
                            continue
                        try:
                            print(f"Running {config['name']} test {wrk_test['name']}")
                            wrk_process = subprocess.run(
                                wrk_test["wrk_command"],
                                shell=True,
                                stdout=subprocess.PIPE,
                            )
                            result = BenchResult.create_from_wrk_output(
                                webserver_name=config["name"],
                                language=config["language"],
                                test_name=wrk_test["name"],
                                database=database_name(run_option, wrk_test["name"]),
                                orm=run_option.get("orm") if wrk_test['name'] not in STATELESS_TEST_NAMES else None,
                                output=wrk_process.stdout,
                            )
                            summary.results.append(result)
                            finished.add(f"{config['name']}_{wrk_test['name']}")
                        except Exception as e:
                            errors.append(f"Failed to run {wrk_test['name']} test {e}")
                finally:
                    errors.append(f"terminate webserver {web_server_process.pid}")
                    p = psutil.Process(web_server_process.pid)
                    for child in p.children(recursive=True):
                        try:
                            child.kill()
                        except Exception as e:
                            errors.append("Failed to kill child process: " + str(e))
                    p.kill()
                    time.sleep(5)
        except FileNotFoundError:
            errors.append(f"Skipping {web_server} as it doesn't have a config.toml file")
            continue

    print("Done")
    with open(f"reports/{summary.created_at}.json", "w") as f:
        f.write(summary.json())
    with open(f"reports/{summary.created_at}_error.txt", "w") as f:
        for e in errors:
            f.write(f"{e}\n")

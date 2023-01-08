import datetime
import os
import subprocess
import time
from pathlib import Path

import psutil
import pydantic
import tomllib

web_servers_path = Path("web_servers")

WRK_COMMAND = "wrk -t2 -c100 -d30s --latency -s ./wrk_scripts/{script_name} http://127.0.0.1:8000/"
GET_USER_BENCH = dict(name="get user", wrk_command=WRK_COMMAND.format(script_name="get_user_by_pk.lua"))
UPDATE_USER_BENCH = dict(name="update user", wrk_command=WRK_COMMAND.format(script_name="update_user.lua"))
PLAIN_TEXT_BENCH = dict(name="plain", wrk_command=WRK_COMMAND.format(script_name="plain.lua"))
TO_JSON_BENCH = dict(name="to json", wrk_command=WRK_COMMAND.format(script_name="to_json.lua"))
WRK_TESTS = [GET_USER_BENCH, UPDATE_USER_BENCH, TO_JSON_BENCH, PLAIN_TEXT_BENCH]


class BenchResult(pydantic.BaseModel):
    test_name: str
    webserver_name: str
    database: str
    orm: bool

    requests_per_second: float
    latency_p50: str
    latency_p75: str
    latency_p90: str
    latency_p99: str

    @classmethod
    def create_from_wrk_output(
        cls, webserver_name: str, test_name: str, database: str, orm: bool, output: str
    ) -> "BenchResult":
        data = output.splitlines()
        return cls(
            test_name=test_name,
            webserver_name=webserver_name,
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
    time.sleep(1)


if __name__ == "__main__":
    print("Running benchmarks")
    summary = BenchSummary(created_at=datetime.date.today(), results=[])

    for web_server in web_servers_path.iterdir():
        try:
            with open(f"{web_server}/config.toml", "rb") as f:
                config = tomllib.load(f)

            for run_setup_name, run_option in config["run_options"].items():
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
                    time.sleep(5)
                    for wrk_test in WRK_TESTS:
                        try:
                            print(f"Running {config['name']} test {wrk_test['name']}")
                            wrk_process = subprocess.run(
                                wrk_test["wrk_command"],
                                shell=True,
                                stdout=subprocess.PIPE,
                            )
                            result = BenchResult.create_from_wrk_output(
                                webserver_name=config["name"],
                                test_name=wrk_test["name"],
                                database=run_option["database"],
                                orm=run_option["orm"],
                                output=wrk_process.stdout,
                            )
                            summary.results.append(result)
                        except Exception as e:
                            print(f"Failed to run {wrk_test['name']} test {e}")
                finally:
                    print(f"terminate webserver {web_server_process.pid}")
                    p = psutil.Process(web_server_process.pid)
                    for child in p.children(recursive=True):
                        try:
                            child.kill()
                        except Exception:
                            pass
                    p.kill()
                    time.sleep(5)
        except FileNotFoundError:
            print(f"Skipping {web_server} as it doesn't have a config.toml file")
            continue

    print("Done")
    with open(f"reports/{summary.created_at}.json", "w") as f:
        f.write(summary.json())
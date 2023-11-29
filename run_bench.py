import datetime
import os
import subprocess
import time
from pathlib import Path

import psutil
import pydantic
import requests
import tomllib
from loguru import logger

TODAY = datetime.date.today()
LOG_FILE = f"./logs/{TODAY}.log"
LOGGING_FORMAT = format = "{time:HH:mm:ss} {message}"

NUMBER_OF_CONCURRENT_CLIENTS = 100
TEST_LENGHT_IN_SEC = 60
WEBSERVER_ADDRESS = "http://127.0.0.1:8000"


def create_wrk_command(script_name: str) -> str:
    return f"wrk -t2 -c{NUMBER_OF_CONCURRENT_CLIENTS} -d{TEST_LENGHT_IN_SEC}s --latency -s ./wrk_scripts/{script_name} {WEBSERVER_ADDRESS}"


class Scenario(pydantic.BaseModel):
    name: str
    wrk_command: str


GET_USER_BENCH = Scenario(
    name="get user", wrk_command=create_wrk_command(script_name="get_user_by_pk.lua")
)
UPDATE_USER_BENCH = Scenario(
    name="update user", wrk_command=create_wrk_command(script_name="update_user.lua")
)
PLAIN_TEXT_BENCH = Scenario(
    name="plain", wrk_command=create_wrk_command(script_name="plain.lua")
)
TO_JSON_BENCH = Scenario(
    name="to json", wrk_command=create_wrk_command(script_name="to_json.lua")
)

WRK_TESTS = [GET_USER_BENCH, UPDATE_USER_BENCH, TO_JSON_BENCH, PLAIN_TEXT_BENCH]
STATELESS_TEST_NAMES = [TO_JSON_BENCH.name, PLAIN_TEXT_BENCH.name]


class BenchResult(pydantic.BaseModel):
    test_name: str
    webserver_name: str
    source: str
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
        database: str | None,
        orm: str | None,
        output: str,
        source: str,
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
            source=source,
        )


class BenchSummary(pydantic.BaseModel):
    created_at: datetime.date
    results: list[BenchResult]


def log_subprocess_output(pipe, logger):
    logger.info(pipe.splitlines())
    for line in pipe.splitlines():
        logger.info("got line from subprocess: %r", line)
        print("got line from subprocess: %r", line)


class RunOption(pydantic.BaseModel):
    BUILD_COMMAND: str
    RUN_COMMAND: str
    orm: str | None = None
    database: str | None = None
    db_client: str | None = None


class WebServerConfig(pydantic.BaseModel):
    name: str
    language: str
    run_options: dict[str, RunOption]


class WebServer:
    def __init__(
        self,
        config: WebServerConfig,
        run_option: RunOption,
        path: Path,
        log,
        source: str,
    ) -> None:
        self.config = config
        self.run_option = run_option
        self.path = path
        self.log = log
        self._server_process: psutil.Popen | None = None
        self.source = source

    @classmethod
    def build_and_run(
        cls, config: WebServerConfig, run_option: RunOption, path: Path, log, source: str
    ) -> "WebServer":
        log.debug(f"Build {config.name}")
        os.system(f"cd {path} && {run_option.BUILD_COMMAND}")
        ws = WebServer(config, run_option, path, logger, source)
        log.debug(f"Start webserver {config.name} in subprocess")
        proc = subprocess.Popen(
            [run_option.RUN_COMMAND], shell=True, stdout=subprocess.PIPE
        )
        log.info(f"started {proc.pid}")
        ws._server_process = proc  # type: ignore
        return ws

    def run(self, scenario: Scenario) -> BenchResult:
        self.log.info(f"test {scenario.name}")
        process = subprocess.run(
            scenario.wrk_command, shell=True, stdout=subprocess.PIPE
        )
        return BenchResult.create_from_wrk_output(
            webserver_name=self.config.name,
            language=self.config.language,
            test_name=scenario.name,
            database=database_name(self.run_option, scenario.name),
            orm=self.run_option.orm
            if scenario.name not in STATELESS_TEST_NAMES
            else None,
            output=process.stdout.decode("utf-8"),
            source=self.source,
        )

    def finish(self):
        if not self._server_process:
            raise Exception("Server process is not started")

        self.log.info(f"terminate webserver {self._server_process.pid}")
        p = psutil.Process(self._server_process.pid)
        for child in p.children(recursive=True):
            try:
                child.kill()
            except Exception as e:
                self.log.error("Failed to kill child process: " + str(e))
        p.kill()


def clean_db(logger):
    logger.debug("Clean DB")
    os.system(
        "psql postgresql://postgres:pass@localhost:15432/webservers_bench < postgres_db.sql"
    )
    os.system(
        "mysql --user=user --password=pass --port=13306 --protocol=tcp webservers_bench < mysql_db.sql"
    )
    os.system("python redis_data_generator.py | redis-cli --pipe -p 26379")
    time.sleep(1)


def database_name(config: RunOption, test_name: str | None) -> str | None:
    if test_name and test_name in STATELESS_TEST_NAMES or not config.database:
        return None
    res = config.database
    if config.db_client:
        res += f"[{config.db_client}]"
    return res


def load_webserver(ws_path: Path, logger) -> WebServerConfig:
    filename = f"{ws_path}/config.toml"
    with open(filename, "rb") as f:
        raw_config = tomllib.load(f)
        try:
            return WebServerConfig(**raw_config)
        except Exception as e:
            logger.error(raw_config)
            raise e


def check_service(logger):
    cnt = 300
    start_at = datetime.datetime.now()
    while cnt > 0:
        try:
            ping_res = requests.get(f"{WEBSERVER_ADDRESS}/ping/")
            if ping_res.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.1)
        cnt -= 1
    finish_at = datetime.datetime.now()
    logger.error(f"Can't start webserver in {(finish_at - start_at).seconds} sec")


if __name__ == "__main__":
    logger.add(LOG_FILE, format=LOGGING_FORMAT)
    log = logger.bind(webserver="root")
    log.info("Running benchmarks")

    sha_commit = subprocess.run(
        "git rev-parse --short HEAD", shell=True, stdout=subprocess.PIPE
    ).stdout.decode("utf-8").strip()

    summary = BenchSummary(created_at=TODAY, results=[])
    errors = []
    for web_server_path in Path("web_servers").iterdir():
        try:
            source = f"https://github.com/antonguzun/webservers_benchmark/blob/{sha_commit}/{web_server_path}/config.toml"
            config = load_webserver(web_server_path, log)

            finished = set()
            for run_setup_name, run_option in config.run_options.items():
                if config.name in ("hyper[sync]",):
                    continue

                log.debug(f"Running benchmarks for {config.name} {run_setup_name}")
                clean_db(log)

                web_server = WebServer.build_and_run(
                    config, run_option, web_server_path, log, source
                )

                try:
                    for wrk_test in WRK_TESTS:
                        scenario_key = f"{config.name}_{wrk_test.name}"

                        log.info(f"check webserver {scenario_key}")
                        check_service(log)
                        if (
                            wrk_test.name in STATELESS_TEST_NAMES
                            and scenario_key in finished
                        ):
                            continue

                        try:
                            result = web_server.run(wrk_test)

                            summary.results.append(result)
                            finished.add(scenario_key)
                        except Exception as e:
                            log.error(
                                f"Failed to run {scenario_key} cause of error: {e}"
                            )

                finally:
                    web_server.finish()  # type: ignore
                    time.sleep(5)

        except Exception as e:
            log.warning(f"Skipping {web_server_path} cause of error: {e}")
            continue

    with open(f"reports/{summary.created_at}.json", "w") as f:
        f.write(summary.model_dump_json())

    log.info("Done")

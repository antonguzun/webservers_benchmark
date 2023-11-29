from pathlib import Path

import requests
from loguru import logger

from run_bench import (
    LOG_FILE,
    LOGGING_FORMAT,
    WebServer,
    check_service,
    clean_db,
    load_webserver,
    WEBSERVER_ADDRESS,
)


def test_to_json(config):
    log_key = f"{config.name} to_json"
    url = f"{WEBSERVER_ADDRESS}/to_json?param1=12345&param2=ZXCV&param3=QWERASD"
    res = requests.get(url)
    assert res.status_code == 403, f"{log_key} should be forbidden without token"

    res = requests.get(url, headers={"token": "hardcoded_token"})
    assert res.status_code == 200, f"{log_key} wrong status code"
    log.info(f"{log_key} {res.json()}")
    assert res.json() == {
        "param1": "12345",
        "param2": "ZXCV",
        "param3": "QWERASD",
    }, f"{log_key} wrong response"


def test_plain(config):
    log_key = f"{config.name} plain"
    log.info(f"Starting {log_key}")

    url = f"{WEBSERVER_ADDRESS}/plain?param1=12345&param2=ZXCV&param3=QWERASD"
    res = requests.get(url)
    assert res.status_code == 403, "should be forbidden without token"

    res = requests.get(url, headers={"token": "hardcoded_token"})
    assert res.status_code == 200, "wrong status code"
    log.info(f"{log_key} {res.text}")
    assert res.text == "param1=12345, param2=ZXCV, param3=QWERASD", "wrong response"


def test_get_user(config):
    log_key = f"{config.name} get user"
    log.info(f"Starting {log_key}")

    url = f"{WEBSERVER_ADDRESS}/user/5/"
    res = requests.get(url)
    assert res.status_code == 403, "should be forbidden without token"

    res = requests.get(url, headers={"token": "hardcoded_token"})
    assert res.status_code == 200, "wrong status code"
    res_json = res.json()
    log.info(f"{log_key} {res_json}")
    assert res_json["user_id"] == 5
    assert "username" in res_json and len(res_json["username"]) > 0
    assert "email" in res_json and len(res_json["email"]) > 0
    assert "created_at" in res_json and len(res_json["created_at"]) > 0
    assert res_json["is_archived"] is False


def test_update_user(config):
    log_key = f"{config.name} get user"
    log.info(f"Starting {log_key}")

    url = f"{WEBSERVER_ADDRESS}/user/5/"
    res = requests.get(url)
    assert res.status_code == 403, "should be forbidden without token"

    res = requests.patch(
        url,
        headers={"token": "hardcoded_token"},
        json={"username": "test_username", "email": "asdf@gmail.com"},
    )
    assert res.status_code == 200, "wrong status code"
    res_json = res.json()
    log.info(f"{log_key} {res_json}")
    assert res_json["user_id"] == 5
    assert res_json["username"] == "test_username"
    assert res_json["email"] == "asdf@gmail.com"
    assert "created_at" in res_json and len(res_json["created_at"]) > 0
    assert res_json["is_archived"] is False


if __name__ == "__main__":
    logger.add(LOG_FILE, format=LOGGING_FORMAT)
    log = logger.bind(webserver="root")
    log.info("Running tests")

    clean_db(log)

    for web_server_path in Path("web_servers").iterdir():
        config = load_webserver(web_server_path, log)

        for run_setup_name, run_option in config.run_options.items():
            web_server = WebServer.build_and_run(
                config, run_option, web_server_path, log
            )

            try:
                check_service(log)
                test_to_json(config)
                test_plain(config)
                test_get_user(config)
                test_update_user(config)
            except Exception as e:
                log.exception("During test")
                raise e
            finally:
                web_server.finish()

    log.info("Done")

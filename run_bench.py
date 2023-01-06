import os
import signal
import subprocess
import time
from pathlib import Path
from textwrap import dedent

import tomllib

web_servers_path = Path("web_servers")

if __name__ == "__main__":
    print("Running benchmarks")

    for web_server in web_servers_path.iterdir():
        try:
            with open(f"{web_server}/config.toml", "rb") as f:
                config = tomllib.load(f)
                print(f"Running benchmarks for {config['name']}")
                print(f"Build {config['name']}")
                os.system(f"cd {web_server} && {config['BUILD_COMMAND']}")
                print(f"Run webserver {config['name']} in subprocess")
                web_server_process = subprocess.Popen(
                    [f"PYTHONPATH=./{web_server} ./{web_server}/venv/bin/uvicorn src.main:app --workers 8 > /dev/null"],
                    shell=True,
                )
                print(f"started {web_server_process.pid}")
                try:
                    time.sleep(5)
                    wrk_process = subprocess.run(
                        "wrk -t2 -c100 -d30s --latency -s ./wrk_scripts/get_user_by_pk.lua http://127.0.0.1:8000/",
                        shell=True,
                        stdout=subprocess.PIPE,
                    )
                    print("wrk output:")
                    print(wrk_process.stdout)
                finally:
                    print(f"terminate {web_server_process.pid}")
                    a = subprocess.run(
                        "ps a | grep './web_servers/py_fast_api/venv/bin/uvicorn'", shell=True, stdout=subprocess.PIPE
                    )

                    pids = [int(i.split()[0]) for i in dedent(a.stdout.decode()).splitlines()]
                    for pid in pids:
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except Exception:
                            pass
                    print(a)
                    time.sleep(5)
        except FileNotFoundError:
            print(f"Skipping {web_server} as it doesn't have a config.toml file")
            continue

    print("Done")

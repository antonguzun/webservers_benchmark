import os
import subprocess
from statistics import mean

import pydantic


class Point(pydantic.BaseModel):
    t: float
    cu: float
    mu: float


class MonitoringResult(pydantic.BaseModel):
    mean_cpu_usage: float
    mean_memory_usage: float
    points: list[Point]


class WebServerMonitor:
    interval_sec = 0.1

    def __init__(self, webserver_pid: int, scenario_name: str):
        self.webserver_pid = webserver_pid
        self.scenario_name = scenario_name
        self.filename = f"./logs/{webserver_pid}-{scenario_name.replace(' ', '-')}.log"
        self._monitor_proc = None

    def __enter__(self):
        self._monitor_proc = subprocess.Popen(
            [
                f"./venv/bin/psrecord {self.webserver_pid} --include-children --log {self.filename} --interval={self.interval_sec}"
            ],
            shell=True,
        )

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._monitor_proc:
            raise Exception("Monitor process is not started")

        self._monitor_proc.kill()

    def parse_results(self) -> MonitoringResult:
        points = []
        try:
            with open(self.filename) as f:
                f.readline()  # skip header
                for line in f.readlines():
                    values = line.strip().split(" ")
                    filtered_values = []
                    for v in values:
                        if v:
                            filtered_values.append(v)
                    time, cpu, memory, _ = filtered_values
                    points.append(
                        Point(
                            t=float(time.strip()),
                            cu=float(cpu.strip()),
                            mu=float(memory.strip()),
                        )
                    )
        except Exception as e:
            print(e)
        finally:
            os.remove(self.filename)

        return MonitoringResult(
            mean_cpu_usage=round(mean([p.cu for p in points]), 2),
            mean_memory_usage=round(mean([p.mu for p in points]), 2),
            points=points,
        )

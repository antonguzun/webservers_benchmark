import os
from enum import Enum

import sentry_sdk

DEBUG = False

MYSQL_URI = os.environ.get("MYSQL_URI", "fake")
POSTGRES_URI = os.environ.get("POSTGRES_URI", "postgresql://postgres:pass@localhost:15432/webservers_bench")


class Databases(str, Enum):
    MYSQL_ALCHEMY = "mysql_alchemy"
    POSTGRES_ALCHEMY = "postgres_alchemy"
    POSTGRES_RAW = "postgres_raw"


CHOSEN_DB = os.environ["DATABASE"]

match CHOSEN_DB:
    case Databases.MYSQL_ALCHEMY:
        DATABASE_URI = MYSQL_URI
    case Databases.POSTGRES_ALCHEMY:
        DATABASE_URI = "postgresql+asyncpg://postgres:pass@localhost:15432/webservers_bench"
    case Databases.POSTGRES_RAW:
        DATABASE_URI = "postgresql://postgres:pass@localhost:15432/webservers_bench"
    case _:
        raise NotImplementedError(f"Database not implemented: {CHOSEN_DB}")

RABBITMQ_URI = os.environ.get("RABBITMQ_URI", "fake")


sentry_sdk.init(dsn="")

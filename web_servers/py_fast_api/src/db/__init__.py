from src.settings import CHOSEN_DB, Databases

match CHOSEN_DB:
    case Databases.MYSQL_ALCHEMY:
        from . import mysql as db_module
    case Databases.MYSQL_RAW:
        from . import mysql_raw as db_module
    case Databases.POSTGRES_ALCHEMY:
        from . import postgres as db_module
    case Databases.POSTGRES_RAW:
        from . import postgres_asyncpg as db_module
    case _:
        raise NotImplementedError()

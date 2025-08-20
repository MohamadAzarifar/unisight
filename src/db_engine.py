import sqlite3
import requests
from sqlalchemy import StaticPool, create_engine


class ChinookDBEngineSingleton:
    _instance = None

    @classmethod
    def get_engine(cls):
        if cls._instance is None:
            url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
            response = requests.get(url)
            sql_script = response.text
            connection = sqlite3.connect(":memory:", check_same_thread=False)
            connection.executescript(sql_script)
            cls._instance = create_engine(
                "sqlite://",
                creator=lambda: connection,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
            )
        return cls._instance
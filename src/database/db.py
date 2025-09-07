import json
from sqlalchemy import create_engine, inspect


class AppDb:
    def __init__(self, db_url):
        self.__db_url = db_url
        engine = create_engine(self.__db_url)
        self.inspect = inspect(engine)

    def extract_schema(self):
        schema = {}

        for table in self.inspect.get_table_names():
            columns = self.inspect.get_columns(table)
            schema[table] = [col["name"] for col in columns]

        return json.dumps(schema, indent=1)

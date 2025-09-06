import json
from frontend.chat import AppChat
from backend.llm import AppLLM
from sqlalchemy import create_engine, inspect


class App:
    def __init__(self):
        model = "qwen3:0.6b"
        db_url = "postgresql://postgres:chinook@localhost:55000/chinook"
        self.llm = AppLLM(model)
        self.chat = AppChat(self.llm)
        schema = self.extract_schema(db_url)
        self.chat.json(schema)

    def extract_schema(self, db_url):
        engine = create_engine(db_url)
        inspector = inspect(engine)
        schema = {}

        for table in inspector.get_table_names():
            columns = inspector.get_columns(table)
            schema[table] = [col["name"] for col in columns]

        return json.dumps(schema, indent=1)

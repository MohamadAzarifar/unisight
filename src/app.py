from frontend.chat import AppChat
from backend.llm import AppLLM
from database.db import AppDb


class App:
    def __init__(self):
        model = "qwen3:0.6b"
        db_url = "postgresql://postgres:chinook@localhost:55000/chinook"

        self.llm = AppLLM(model)
        self.chat = AppChat(self.llm)
        self.db = AppDb(db_url)
        schema = self.db.extract_schema()
        self.chat.json(schema)

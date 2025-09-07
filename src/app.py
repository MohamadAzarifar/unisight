from backend.llm import AppLLM
from database.db import AppDb
from frontend.intereface import AppInterface


class App:
    def __init__(self, model, db_url):
        self.db = AppDb(db_url)
        self.llm = AppLLM(model)
        self.chat = AppInterface(self.llm)

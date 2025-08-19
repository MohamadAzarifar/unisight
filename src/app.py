from enum import Enum
import time
import datetime
import sqlite3
import requests

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import streamlit as st

from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from langgraph.prebuilt import create_react_agent

LLMS = [
    "gpt-oss:20b",
    "llama3.1",
    "qwen3:0.6b",
    "gemma3n:e4b",
    "deepseek-r1",
    "sqlcoder",
]


# --- Session State Keys ---
class SessionStateKeys(Enum):
    ISTIMECHECKED = "ISTIMECHECKED"
    LETSLOGIN = "LETSLOGIN"
    VISIT_TIME = "VISIT_TIME"
    IS_AUTHENTICATED = "IS_AUTHENTICATED"
    USERNAME = "USERNAME"
    PASSWORD = "PASSWORD"
    ENVIRONMENT = "ENVIRONMENT"
    ENVSELECTED = "ENVSELECTED"
    CHATHISTORY = "CHATHISTORY"
    DBTABLES = "DBTABLES"
    LLMSELECTED = "LLMSELECTED"
    LLM = "LLM"

    def get(self):
        return st.session_state.get(self.value, None)

    def set(self, value):
        st.session_state[self.value] = value


def initialize_session_state():
    defaults = {
        SessionStateKeys.ISTIMECHECKED: False,
        SessionStateKeys.LETSLOGIN: False,
        SessionStateKeys.VISIT_TIME: datetime.datetime.now(),
        SessionStateKeys.IS_AUTHENTICATED: False,
        SessionStateKeys.ENVSELECTED: False,
        SessionStateKeys.CHATHISTORY: [],
        SessionStateKeys.DBTABLES: False,
        SessionStateKeys.LLMSELECTED: False,
        SessionStateKeys.LLM: LLMS[0],
    }
    for key, value in defaults.items():
        if key.get() is None:
            key.set(value)


# --- Static Messages ---
class StaticMessages(Enum):
    CURRENT_TIME = "It is {time} right now."
    ARRIVED_TIME = "You arrived at: {time}."
    ERROR_LOGIN = "🫠 Login failed. Please check your username and password."
    INFO_LOGIN = "🤗 Please login to continue."
    SUCCESS_LOGIN = "Nice to meet you {username} 😍. Use the _logout_ button to go back to the login form."
    ENVIRONMENT = "connected to {environment} database."
    LOGIN_BTN = "Login"
    LOGOUT_BTN = "Logout"


# --- Authentication ---
def authenticate() -> bool:
    SessionStateKeys.IS_AUTHENTICATED.set(False)
    username = SessionStateKeys.USERNAME.get()
    password = SessionStateKeys.PASSWORD.get()
    if username and password and len(username) > 5 and len(password) > 5:
        SessionStateKeys.IS_AUTHENTICATED.set(True)
        return True
    st.toast(StaticMessages.ERROR_LOGIN.value)
    return False


def logout():
    SessionStateKeys.USERNAME.set("")
    SessionStateKeys.PASSWORD.set("")
    SessionStateKeys.IS_AUTHENTICATED.set(False)
    SessionStateKeys.ENVSELECTED.set(False)
    SessionStateKeys.DBTABLES.set(False)
    SessionStateKeys.CHATHISTORY.set([])


# --- Database ---
def get_engine_for_chinook_db():
    url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
    response = requests.get(url)
    sql_script = response.text
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(sql_script)
    return create_engine(
        "sqlite://",
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )


# --- Chat ---
def chat_stream(prompt: str, agent_executor):
    events = agent_executor.stream(
        {"messages": [("user", prompt)]},
        stream_mode="values",
    )
    response = ""
    for event in events:
        msg = event["messages"][-1].content if event["messages"] else ""
        response += msg
        yield msg
        time.sleep(0.02)
    return response


# def chat_stream(prompt: str):
# llm = ChatOllama(model=SessionStateKeys.LLM.get(), reasoning=False)
# response = llm.invoke(prompt).content
# for char in response:
#     yield char
#     time.sleep(0.02)


def save_feedback(index):
    SessionStateKeys.CHATHISTORY.get()[index]["feedback"] = st.session_state[
        f"feedback_{index}"
    ]


# --- UI Components ---
def display_current_timer():
    with st.chat_message("assistant", avatar="🕐"):
        st.write(
            StaticMessages.CURRENT_TIME.value.format(
                time=datetime.datetime.now().strftime("%H:%M:%S")
            )
        )


def display_arrived_time():
    with st.chat_message("assistant"):
        st.write(
            StaticMessages.ARRIVED_TIME.value.format(
                time=SessionStateKeys.VISIT_TIME.get().strftime("%d/%M/%Y %H:%M")
            )
        )


def login_form():
    st.header(StaticMessages.INFO_LOGIN.value)
    SessionStateKeys.USERNAME.set("")
    SessionStateKeys.PASSWORD.set("")
    username = st.text_input(
        "Username",
        key="username",
        placeholder="Enter your username",
        value=SessionStateKeys.USERNAME.get(),
    )
    SessionStateKeys.USERNAME.set(username)
    password = st.text_input(
        "Password",
        key="password",
        placeholder="Enter your password",
        type="password",
        value=SessionStateKeys.PASSWORD.get(),
    )
    SessionStateKeys.PASSWORD.set(password)
    st.button(
        StaticMessages.LOGIN_BTN.value,
        width="stretch",
        on_click=authenticate,
    )


def show_success_login():
    with st.chat_message("assistant"):
        container = st.container(horizontal=True)
        container.write(
            StaticMessages.SUCCESS_LOGIN.value.format(
                username=SessionStateKeys.USERNAME.get()
            )
        )
        container.button(
            StaticMessages.LOGOUT_BTN.value,
            on_click=logout,
        )


def environment_selector():
    with st.chat_message("assistant", avatar="💾"):
        environment = st.selectbox(
            "Environment",
            ["Unimics", "Sample", "Hyperfamily"],
            disabled=SessionStateKeys.ENVSELECTED.get(),
        )
        SessionStateKeys.ENVIRONMENT.set(environment)
        st.write(
            StaticMessages.ENVIRONMENT.value.format(
                environment=SessionStateKeys.ENVIRONMENT.get(),
            )
        )
        if not SessionStateKeys.ENVSELECTED.get():
            st.button(
                "Let's go",
                on_click=lambda: SessionStateKeys.ENVSELECTED.set(True),
            )


def llm_selector():
    with st.chat_message("assistant", avatar="💾"):
        llm = st.selectbox("Language Model", LLMS)
        SessionStateKeys.LLM.set(llm)
        if not SessionStateKeys.LLMSELECTED.get():
            st.button(
                "Let's go",
                on_click=lambda: SessionStateKeys.LLMSELECTED.set(True),
            )


def show_database_details(DATABASE):
    with st.chat_message("ai"):
        st.write(
            "Let's learn more about the structure of information stored in a database."
        )
        st.button(
            f"The tables of {SessionStateKeys.ENVIRONMENT.get()}'s database",
            on_click=lambda: SessionStateKeys.DBTABLES.set(
                not SessionStateKeys.DBTABLES.get()
            ),
        )
    if SessionStateKeys.DBTABLES.get():
        st.write(DATABASE.get_table_names())


def chat_history_ui():
    for i, message in enumerate(SessionStateKeys.CHATHISTORY.get()):
        with st.chat_message(message["role"]):
            st.write(message["content"])
        if message["role"] == "assistant":
            feedback = message.get("feedback", None)
            st.session_state[f"feedback_{i}"] = feedback
            st.feedback(
                "thumbs",
                key=f"feedback_{i}",
                on_change=save_feedback,
                args=[i],
            )


def chat_input_ui(agent_executor):
    prompt = st.chat_input("Let's talk about the business...")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.CHATHISTORY.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            response = st.write_stream(chat_stream(prompt, agent_executor))
            st.feedback(
                "thumbs",
                key=f"feedback_{len(st.session_state.CHATHISTORY)}",
                on_change=save_feedback,
                args=[len(st.session_state.CHATHISTORY)],
            )
        st.session_state.CHATHISTORY.append({"role": "assistant", "content": response})


# def chat_input_ui():
#     prompt = st.chat_input("Let's talk about the business...")
#     if prompt:
#         with st.chat_message("user"):
#             st.write(prompt)
#         st.session_state.CHATHISTORY.append({"role": "user", "content": prompt})
#         with st.chat_message("assistant"):
#             response = st.write_stream(chat_stream(prompt))
#             st.feedback(
#                 "thumbs",
#                 key=f"feedback_{len(st.session_state.CHATHISTORY)}",
#                 on_change=save_feedback,
#                 args=[len(st.session_state.CHATHISTORY)],
#             )
#         st.session_state.CHATHISTORY.append({"role": "assistant", "content": response})


# --- Main App ---
def main():
    st.title("🪐 UNISIGHT")
    initialize_session_state()
    engine = get_engine_for_chinook_db()
    DATABASE = SQLDatabase(engine)

    # Instantiate llm after user selects LLM
    LLM = ChatOllama(model=SessionStateKeys.LLM.get(), reasoning=False)

    # Inject SQLDatabaseToolkit here
    TOOLKIT = SQLDatabaseToolkit(db=DATABASE, llm=LLM)

    # prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
    prompt_template = """
You are an agent designed to interact with a SQL database.
Consider the database schema consists of these tables: {tables}
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

To start you should ALWAYS look at the tables in the database to see what you can query.
Do NOT skip this step.
Then you should query the schema of the most relevant tables.
""".format(
        tables=DATABASE.get_context,
        dialect=DATABASE.dialect,
        top_k=5,
    )

    agent_executor = create_react_agent(
        LLM, TOOLKIT.get_tools(), prompt=prompt_template
    )

    display_current_timer()

    if not SessionStateKeys.ISTIMECHECKED.get():
        st.button(
            "Time checked 👍",
            on_click=lambda: SessionStateKeys.ISTIMECHECKED.set(True),
            disabled=SessionStateKeys.ISTIMECHECKED.get(),
        )

    if SessionStateKeys.ISTIMECHECKED.get():
        display_arrived_time()

    if SessionStateKeys.ISTIMECHECKED.get() and not SessionStateKeys.LETSLOGIN.get():
        st.button(
            "Lets Login 🤝", on_click=lambda: SessionStateKeys.LETSLOGIN.set(True)
        )

    if (
        SessionStateKeys.ISTIMECHECKED.get()
        and SessionStateKeys.LETSLOGIN.get()
        and not SessionStateKeys.IS_AUTHENTICATED.get()
    ):
        login_form()

    if (
        SessionStateKeys.ISTIMECHECKED.get()
        and SessionStateKeys.LETSLOGIN.get()
        and SessionStateKeys.IS_AUTHENTICATED.get()
    ):
        show_success_login()

    if SessionStateKeys.IS_AUTHENTICATED.get():
        environment_selector()

    if SessionStateKeys.ENVSELECTED.get():
        llm_selector()

    if SessionStateKeys.LLMSELECTED.get():
        show_database_details(DATABASE)
        chat_history_ui()
        chat_input_ui(agent_executor)


if __name__ == "__main__":
    main()

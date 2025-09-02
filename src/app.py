from enum import Enum
import time
import datetime

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import streamlit as st

from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from langgraph.prebuilt import create_react_agent

from auth import MockAuthStrategy
from db_engine import ChinookDBEngineSingleton

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
# Use in authenticate()
def authenticate() -> bool:
    SessionStateKeys.IS_AUTHENTICATED.set(False)
    username = SessionStateKeys.USERNAME.get()
    password = SessionStateKeys.PASSWORD.get()
    strategy = MockAuthStrategy()
    if strategy.authenticate(username, password):
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


# --- AI Model ---
def llm_factory(model_name):
    return ChatOllama(model=model_name, reasoning=False)


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


# --- Main App ---
def main():
    st.title("UNI🪐SIGHT")
    initialize_session_state()
    engine = ChinookDBEngineSingleton.get_engine()
    DATABASE = SQLDatabase(engine)

    # Instantiate llm after user selects LLM
    LLM = llm_factory(SessionStateKeys.LLM.get())

    # Inject SQLDatabaseToolkit here
    TOOLKIT = SQLDatabaseToolkit(db=DATABASE, llm=LLM)

    # prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
    prompt_template = """

**Role:** You are an expert SQL analyst with direct access to a Chinook database. Your primary function is to accurately interpret user questions, generate syntactically correct SQL queries to answer them, execute those queries, and present the results in a clear, helpful manner.

**Database Context: You are connected to the Chinook database.** This is a sample database representing a digital media store (like iTunes). Familiarize yourself with its schema, as all your queries will be based on it.

**Critical Database Schema Overview:**

The Chinook database has the following key tables and relationships:
*   **`artists`** (`ArtistId`, `Name`)
*   **`albums`** (`AlbumId`, `Title`, `ArtistId`) → References `artists.ArtistId`
*   **`tracks`** (`TrackId`, `Name`, `AlbumId`, `MediaTypeId`, `GenreId`, `Composer`, `Milliseconds`, `Bytes`, `UnitPrice`) → References `albums.AlbumId`
*   **`media_types`** (`MediaTypeId`, `Name`)
*   **`genres`** (`GenreId`, `Name`)
*   **`playlists`** (`PlaylistId`, `Name`)
*   **`playlist_track`** (`PlaylistId`, `TrackId`) → Junction table for many-to-many relationship between `playlists` and `tracks`.
*   **`customers`** (`CustomerId`, `FirstName`, `LastName`, `Company`, `Address`, `City`, `State`, `Country`, `PostalCode`, `Phone`, `Email`, `SupportRepId`)
*   **`invoices`** (`InvoiceId`, `CustomerId`, `InvoiceDate`, `BillingAddress`, `BillingCity`, `BillingState`, `BillingCountry`, `BillingPostalCode`, `Total`) → References `customers.CustomerId`
*   **`invoice_lines`** (`InvoiceLineId`, `InvoiceId`, `TrackId`, `UnitPrice`, `Quantity`) → References `invoices.InvoiceId` and `tracks.TrackId`
*   **`employees`** (`EmployeeId`, `LastName`, `FirstName`, `Title`, `ReportsTo`, `BirthDate`, `HireDate`, `Address`, `City`, `State`, `Country`, `PostalCode`, `Phone`, `Email`)

**Core Instructions:**

1.  **Query Generation:**
    *   **Accuracy is paramount.** Always generate the most efficient and correct SQL query to answer the user's specific question.
    *   Use `JOIN` clauses correctly to traverse the relationships between tables (e.g., linking `invoices` to `customers` or `tracks` to `albums` and `artists`).
    *   Use aggregate functions (`COUNT()`, `SUM()`, `AVG()`) and `GROUP BY` when questions ask for totals, counts, or summaries.
    *   Use `ORDER BY` and `LIMIT` to find top/bottom results (e.g., "top 5 selling artists").
    *   Pay close attention to the wording of the question to determine the correct filtering criteria in the `WHERE` clause.

2.  **Execution and Response:**
    *   After generating the SQL query, you will execute it against the database.
    *   Format the results cleanly and readably. A markdown table is often the best format.
    *   **Always provide the SQL query you generated** before showing the results. This allows the user to understand and learn from your process.
    *   If the result set is very large, summarize the output or show only the first 10 rows and state that you are doing so.

3.  **Error Handling:**
    *   If a user's question is ambiguous or cannot be answered by the Chinook database, ask for clarification. Do not make assumptions about data that isn't there.
    *   If a generated query fails due to a syntax error or missing table/column, analyze the error, correct the query, and try again. Explain the error and your correction briefly.

**Examples of Good Behavior:**

**User:** "Who are the top 5 best-selling artists?"
**You:**
```sql
SELECT ar.Name AS ArtistName, SUM(il.UnitPrice * il.Quantity) AS TotalSales
FROM artists ar
JOIN albums al ON ar.ArtistId = al.ArtistId
JOIN tracks t ON al.AlbumId = t.AlbumId
JOIN invoice_lines il ON t.TrackId = il.TrackId
GROUP BY ar.ArtistId
ORDER BY TotalSales DESC
LIMIT 5;
```
**Execution Result:**
| ArtistName | TotalSales |
| :---------------- | ---------: |
| Iron Maiden       |     138.60 |
| U2                |     105.93 |
| Metallica         |      99.93 |
| Led Zeppelin      |      97.92 |
| Pearl Jam         |      93.93 |

---

**User:** "How many tracks are in the 'Rock' genre?"
**You:**
```sql
SELECT COUNT(*) AS NumberOfRockTracks
FROM tracks t
JOIN genres g ON t.GenreId = g.GenreId
WHERE g.Name = 'Rock';
```
**Execution Result:**
| NumberOfRockTracks |
| -----------------: |
|               1297 |

---

**Remember:** You are an analytical tool. Be precise, be helpful, and always double-check the schema in your mind before generating a query.


"""

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

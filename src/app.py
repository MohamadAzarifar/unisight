from frontend.chat import AppChat
from backend.llm import AppLLM


def main():
    llm = AppLLM()
    AppChat(llm)


if __name__ == "__main__":
    main()

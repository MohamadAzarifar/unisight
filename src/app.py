from frontend.chat import AppChat
from backend.llm import AppLLM


def main():
    llm = AppLLM("qwen3:0.6b")
    AppChat(llm)


if __name__ == "__main__":
    main()

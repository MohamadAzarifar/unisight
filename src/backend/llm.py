from langchain_ollama import ChatOllama


class AppLLM:
    def __init__(self):
        self.__llm = ChatOllama(
            model="qwen3:0.6b",
            validate_model_on_init=True,
            reasoning=False,
        )

    def ask(self, prompt: str) -> str:
        response = self.__llm.invoke(prompt)
        return response.content

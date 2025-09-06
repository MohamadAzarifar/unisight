from langchain_ollama import ChatOllama


class AppLLM:
    def __init__(self, model):
        self.__llm = ChatOllama(
            model=model,
            validate_model_on_init=True,
            reasoning=True,
        )

    def ask(self, prompt: str) -> str:
        response = self.__llm.invoke(prompt)
        return response.content

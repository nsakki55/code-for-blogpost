import controlflow as cf
from langchain_openai import ChatOpenAI


def main():
    cf.default_model = ChatOpenAI(model="gpt-3.5-turbo")
    agent = cf.Agent("Marvin")
    print(agent)
    # assert agent.model.model_name == "gpt-3.5-turbo"

    hello_task = cf.Task("say hello")
    hello_task.run()


main()

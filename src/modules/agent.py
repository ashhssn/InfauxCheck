from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

from dotenv import load_dotenv
import agent_tools
from paddle_ocr import extract_text_from_image

class InfauxAgent:

    def __init__(self):
        tools = [agent_tools.bert_classify, agent_tools.retrieve_from_vs, agent_tools.online_search]
        prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    f"""You are very powerful misinformation detector. First analyze the input text for any signs \
                    of misinformation/disinformation. Step 1: Perform classification using the BERT classifier. \
                    Step 2: Perform the vector similarity search. Step 3: If the similarity search returns a score \
                    lower than 0.5, use the online search tool, with the input text as the query, \
                    to scrape for relevant data to aid in your decision. Given all the outputs, make a decision and \
                    provide evidence as to whether the input is likely true or likely false.""",
                ),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        llm_with_tools = llm.bind_tools(tools)
        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
        )
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    def invoke(self, query: str) -> str:
        response = self.agent_executor.invoke({"input": query})
        return response["output"]

if __name__ == "__main__":
    load_dotenv()
    image_path = "data/images/2024-02-25_3310289540023402853.jpg"  # Replace with your image path
    print("Performing OCR on the image...")
    data = extract_text_from_image(image_path)
    #data = "Over 2.4 million Singaporeans to receive up to S$400 in September to help with cost of living"
    agent = InfauxAgent()
    response = agent.invoke(data)
    print(f"\n {response}")
    

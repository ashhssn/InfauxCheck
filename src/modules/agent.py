from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

from dotenv import load_dotenv
from modules import agent_tools
from modules.paddle_ocr import extract_text_from_image

SYSTEM_PROMPT = """
                        You are a very powerful misinformation detector. You are equipped with certain tools \
                        to assist in analyzing the input any signs of misinformation/disinformation. You have \
                        a routine you follow to ensure all bases are covered when reviewing the input.
                        The routine is as follows:
                        Step 1: Using the BERT Classifier, perform classification on the input text. \
                        If the probability score is not pass 0.6, provide a second opinion. 
                        Step 2: Using the Vector Store, perform a vector similarity search.
                        Step 3: If the similarity score from the similarity search is lower than 0.5, \
                        use the Online Search tool to search up information on the input and use it to \
                        help make your decision.
                        Step 4: Given all outputs from the steps that had occurred, make a decision and \
                        provide supporting evidence that you have found in this routine as to whether the \
                        input is likely true or likely false. \
                        Your output should be HTML friendly, that is all bold text should be enclosed in \
                        <b> </b> tags and all new lines should be enclosed in <br> tags etc.
                """

class InfauxAgent:

    def __init__(self):
        # define tools for agent
        tools = [agent_tools.bert_classify, agent_tools.retrieve_from_vs, agent_tools.online_search]
        # create prompt template
        prompt = ChatPromptTemplate(
            [
                ("system", SYSTEM_PROMPT),
                ("user", "GE2025: Redrawn boundaries in West Coast an 'uphill battle' with short runway to next election, says PSP’s Leong Mun Wai"),
                ("ai", "Based on the input provided, our BERT classifier has given a <b>probability score of 0.91<b/> of it being true. <br> While our RAG search \
                 yieled no results, an online search from CNA has confirmed that the information provided is <b>likely true<b/>. <br> Source: Online search from CNA."),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        # define agent
        llm = ChatOpenAI(model="gpt-4o")
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

    # create method to respond to user input
    def respond(self, query: str) -> str:
        response = self.agent_executor.invoke({"input": query})
        return response["output"]

# only execute if the script is run directly
if __name__ == "__main__":
    load_dotenv()
    image_path = "data/images/2024-02-25_3310289540023402853.jpg"  # Replace with your image path
    print("Performing OCR on the image...")
    data = extract_text_from_image(image_path)
    #data = "Over 2.4 million Singaporeans to receive up to S$400 in September to help with cost of living"
    agent = InfauxAgent()
    response = agent.respond(data)
    print(f"\n {response}")
    

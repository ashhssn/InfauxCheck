from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.agents import tool, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

from bert_classifier import CustomDataset, BERTModel
import torch
from transformers import BertTokenizer
from typing import List
from dotenv import load_dotenv

from online_search import get_search_results, extract_text_from_url
import requests
from bs4 import BeautifulSoup
from googlesearch import search

load_dotenv()

@tool
def bert_classify(data: str):
    """
    Bert model to classify the input string as true or fake news.
    Returns the predicted label, and probability of being true.
    """
    # Load the model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = BERTModel(numcl=1).to(device)
    try:
        model.load_state_dict(torch.load("checkpoints/best_bert_weights.pt", map_location=device), strict=False)
        model.eval()
    except FileNotFoundError:
        raise FileNotFoundError("Model weights file not found. Ensure 'checkpoints/best_bert_weights.pt' exists.")

    # Load the tokenizer
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    # Prepare the data
    dataset = CustomDataset(data, tokenizer, max_len=64)
    loader = torch.utils.data.DataLoader(dataset, batch_size=16)

    for batch in loader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        with torch.no_grad():
            output = model(input_ids, attention_mask)
            output_sigmoid = torch.sigmoid(output)
            prediction = (output_sigmoid >= 0.5).float()

    return prediction, output_sigmoid

@tool
def retrieve_from_vs(data: str):
    """
    Perform similarity search and retrieve the data from the vector store.
    """
    # Initialize the embedding model
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002") #Include API KEY

    # Load the existing Chroma vector store
    vector_store = Chroma(
        collection_name='fact_checker_collection',
        persist_directory='./chroma_db',  # Directory where the database is persisted
        embedding_function=embeddings
    )

    # Perform the similarity search
    search_results = vector_store.similarity_search(query=data, k=5)

    # return top-k results
    return search_results

@tool
def online_search(query: str):
    """
    Searches Google and extracts content from results.
    """
    search_results = get_search_results(query)
    search_data = {}
    
    for url in search_results:
        search_data[url] = extract_text_from_url(url)
    
    return search_data

if __name__ == "__main__":
    data = "Over 2.4 million Singaporeans to receive up to S$400 in September to help with cost of living"
    similarity_threshold = 0.5
    tools = [bert_classify, retrieve_from_vs, online_search]
    prompt = ChatPromptTemplate(
        [
            (
                "system",
                f"""You are very powerful misinformation detector. First analyze the input text for any signs \
                of misinformation/disinformation. Step 1: Perform classification using the BERT classifier. \
                Step 2: Perform the vector similarity search. Step 3: If the similarity search returns a score \
                lower than {similarity_threshold}, use the online search tool, with the input text as the query, \
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
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    response = agent_executor.invoke({"input": data})
    print(f"\n {response['output']}")
    

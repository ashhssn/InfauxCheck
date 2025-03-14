from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.agents import tool
from langchain_core.documents import Document

from modules.bert_classifier import CustomDataset, BERTModel
import torch
from transformers import BertTokenizer
from typing import Tuple, List, Dict

from modules.online_search import get_search_results, extract_text_from_url


@tool
def bert_classify(data: str) -> Tuple[torch.Tensor, torch.Tensor]:
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
def retrieve_from_vs(data: str) -> List[Document]:
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
def online_search(query: str) -> Dict[str, str]:
    """
    Searches Google and extracts content from results.
    """
    search_results = get_search_results(query)
    search_data = {}
    
    for url in search_results:
        search_data[url] = extract_text_from_url(url)
    
    return search_data
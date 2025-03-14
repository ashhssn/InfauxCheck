import requests
from bs4 import BeautifulSoup
from googlesearch import search
from typing import List, Dict

def get_search_results(query: str, num_results: int = 5) -> List[str]:
    """
    Perform a Google search and return the top-k results as URLs.
    """
    search_results = []
    for j in search(query, num_results=num_results):
        search_results.append(j)
    return search_results

def extract_text_from_url(url: str) -> str:
    """
    Scrape the content of a website.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract main content
        paragraphs = soup.find_all('p')
        text = "\n".join([para.get_text() for para in paragraphs])
        return text[:1000]  # Limit output for brevity
    except Exception as e:
        return f"Failed to extract from {url}: {str(e)}"
    
# Main Function 
def online_search_agent(query: str) -> Dict[str, str]:
    """
    Searches Google and extracts content from results.
    """
    print(f"Searching for: {query}")
    
    search_results = get_search_results(query)
    search_data = {}
    
    for url in search_results:
        print(f"\nExtracting from: {url}")
        search_data[url] = extract_text_from_url(url)
    
    return search_data

# Test the function
if __name__ == "__main__":
    user_query = "Over 2.4 million Singaporeans to receive up to S$400 in September to help with cost of living"
    results = online_search_agent(user_query)
    
    # Display results
    for url, content in results.items():
        print(f"\nURL: {url}\nExtracted Content:\n{content[:500]}...\n")
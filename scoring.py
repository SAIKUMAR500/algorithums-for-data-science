!pip install requests beautifulsoup4 sentence-transformers transformers
import requests
from bs4 import BeautifulSoup

from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

def rate_url_validity(user_query: str, url: str) -> dict:
    """
    Evaluates the validity of a given URL by: computing various metrics including
    domain trust, content relevance, fact-checking, bias, and citation scores.

    Args:
        user_query (str): The user's original query
        url (str): The URL to analyze

    Returns:
        dict: A dictionary containing scores for different validity aspects
    """
    
    # Step 1: Fetch Page Content
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = " ".join([p.text for p in soup.find_all("p")])
    except Exception as e:
        return {"error": f"Failed to fetch content: {str(e)}"}

    # Step 2: Domain Authority Check (Placeholder - Replace with Moz API)
    domain_trust = 60  # Replace with actual API call

    # Step 3: Content Relevance (Semantic Similarity)
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    similarity_score = util.pytorch_cos_sim(
        model.encode(user_query), 
        model.encode(page_text)
    ).item() * 100

    # Step 4: Fact-Checking (Google Fact Check API)
    fact_check_score = check_facts(page_text)

    # Step 5: Bias Detection (Sentiment Analysis)
    sentiment_pipeline = pipeline(
        "text-classification", 
        model="cardiffnlp/twitter-roberta-base-sentiment"
    )
    sentiment_result = sentiment_pipeline(page_text[:512])[0]
    bias_score = 100 if sentiment_result["label"] == "POSITIVE" else 50 if sentiment_result["label"] == "NEUTRAL" else 30

    # Step 6: Citation Check (Google Scholar via SerpAPI)
    citation_count = check_google_scholar(url)
    citation_score = min(citation_count * 10, 100)

    # Step 7: Compute Final Score
    final_score = (
        (0.3 * domain_trust) +
        (0.3 * similarity_score) +
        (0.2 * fact_check_score) +
        (0.1 * bias_score) +
        (0.1 * citation_score)
    )

    return {
        "Domain Trust": domain_trust,
        "Content Relevance": similarity_score,
        "Fact-Check Score": fact_check_score,
        "Bias Score": bias_score,
        "Citation Score": citation_score,
        "Final Validity Score": final_score
    }

def check_facts(text: str) -> int:
    """Check factual accuracy using Google Fact Check API"""
    api_url = f"https://toolbox.google.com/factcheck/api/v1/claimsearch?query={text[:200]}"
    try:
        response = requests.get(api_url)
        data = response.json()
        return 80 if "claims" in data and data["claims"] else 40
    except:
        return 50

def check_google_scholar(url: str) -> int:
    """Check Google Scholar citations using SerpAPI"""
    # Replace with your SerpAPI key
    serpapi_key = "09c35361897cc67f2d892ebc8f77f36522233d425b9fc67e4381ac3585f8ae68"
    params = {"q": url, "engine": "google_scholar", "api_key": serpapi_key}
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        return len(data.get("organic_results", []))
    except:
        return -1

if __name__ == "__main__":
    # Example usage
    queries = [
        ("I have just been on an international flight, can I come back home to hold my 1-month-old newborn?", 
         "https://www.bhtp.com/blog/when-safe-to-travel-with-newborn/"),
         
        ("I have just been on an international flight, can I come back home to hold my 1-month-old newborn?", 
         "https://www.quora.com/How-soon-can-I-take-my-newborn-with-me-when-I-fly-internationally"),
         
        ("I have just been on an international flight, can I come back home to hold my 1-month-old newborn?", 
         "https://www.mayoclinic.org/healthy-lifestyle/infant-and-toddler-health/expert-answers/air-travel-with-infant/faq-20058539")
    ]

    for query, url in queries:
        print(f"\nChecking URL: {url}")
        result = rate_url_validity(query, url)
        for k, v in result.items():
            print(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}")


user_prompt = "nvidia stock"
url_to_check = "https://www.google.com/search?q=nvidia+stock+price&rlz=1C5MACD_enUS1130US1130&oq=nvi&gs_lcrp=EgZjaHJvbWUqBggBEEUYOzIGCAAQRRg5MgYIARBFGDsyBwgCEAAYjwIyBwgDEAAYjwIyBggEEEUYPDIGCAUQRRg9MgYIBhBFGDzSAQgzMjIxajBqN6gCALACAA&sourceid=chrome&ie=UTF-8"

result = rate_url_validity(user_prompt, url_to_check)
print(result)




user_prompt = "nvidia stock"
url_to_check = "https://www.cnbc.com/quotes/NVDA"

result = rate_url_validity(user_prompt, url_to_check)
print(result)


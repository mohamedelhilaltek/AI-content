### This module scrape data using the positive and negative words with the help of spacy model for filtering

import requests
from bs4 import BeautifulSoup
import spacy
import os 
from storage import save_scraped_data
import subprocess
import sys
# Load SpaCy NLP model for keyword filtering
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


# API Configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = f"Bearer {os.getenv('GROQ_API_KEY')}"
GROQ_MODEL = "llama3-70b-8192"

def classify_topic_groq(query):
    """
    Use Groq API (LLaMA model) to classify a topic as 'technical' or 'non-technical'.
    This determines whether to include academic content from Arxiv.
    """
    prompt = f"""Classify the following topic as either 'technical' or 'non-technical'.
Only return one word: technical or non-technical.

Topic: {query}
"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers={
            "Authorization": GROQ_API_KEY,
            "Content-Type": "application/json"
        })
        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"].strip().lower()
            return result == "technical"
    except Exception as e:
        print("Groq classification error:", e)

    return False 


def filter_keywords(text, positive_keywords, negative_keywords):
    """
    Filter the text using SpaCy to identify and check for positive and negative keywords.

    Returns:
        bool: True if text contains positive keywords and doesn't contain negative keywords.
    """
    doc = nlp(text)
    
    # Check for negative keywords
    for token in doc:
        if token.text.lower() in [neg.lower() for neg in negative_keywords]:
            return False
    
    # Check for positive keywords
    for token in doc:
        if token.text.lower() in [pos.lower() for pos in positive_keywords]:
            return True

    return False


def duckduckgo_search(query, positive_keywords, negative_keywords):
    """
    Perform a DuckDuckGo search and filter results based on user-defined keywords.
    """
    url = "https://html.duckduckgo.com/html/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.post(url, data={"q": query}, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    for result in soup.find_all("div", class_="result"):
        link_tag = result.find("a", class_="result__a")
        snippet_tag = result.find("a", class_="result__snippet")

        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        link = link_tag["href"]
        description = snippet_tag.get_text(strip=True) if snippet_tag else ""
        combined = f"{title} {description}"

        # Filter the result using SpaCy filtering
        if not filter_keywords(combined, positive_keywords, negative_keywords):
            continue

        results.append({
            "title": title,
            "link": link,
            "description": description,
            "source": "duckduckgo.com"
        })

        if len(results) >= 10:
            break

    return results


def arxiv_search(query):
    """
    Query the Arxiv API for academic results related to the topic.
    """
    base_url = "http://export.arxiv.org/api/query"
    params = {
        'search_query': f'all:{query}',
        'start': 0,
        'max_results': 10,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print("Error fetching from Arxiv")
        return []

    soup = BeautifulSoup(response.text, 'xml')
    entries = soup.find_all('entry')

    results = []
    for entry in entries:
        results.append({
            "title": entry.title.text,
            "link": entry.id.text,
            "description": entry.summary.text,
            "source": "arxiv.org"
        })

    return results


def combine_search_results(query, positive_keywords, negative_keywords):
    """
    Combine DuckDuckGo and (conditionally) Arxiv results based on topic classification.
    """
    # Step 1: Get general web content
    duck_results = duckduckgo_search(query, positive_keywords, negative_keywords)

    # Step 2: Check if the topic is technical enough to include Arxiv
    if classify_topic_groq(query):
        arxiv_results = arxiv_search(query)
    else:
        arxiv_results = []

    

    all_results = duck_results + arxiv_results
    save_scraped_data(all_results)
    return all_results



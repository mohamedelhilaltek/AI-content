# this module focuses on generating ideas from the data scraped and scoring them

import requests
import re
import os
from storage import save_ideas 
# API CONFIGURATION
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = f"Bearer {os.getenv('GROQ_API_KEY')}"
GROQ_MODEL = "llama3-70b-8192"


def generate_ideas_from_article(title, description, source):
    """
    Generates blog post title ideas from a given scraped article using Groq's LLaMA model.
    """
    prompt = f"""
Generate 5 blog post ideas based on the following article.
Each idea should be a standalone blog title, written in one line, not a paragraph.
Avoid phrases like 'In this post', 'We will discuss', etc.
Just return raw blog title ideas — no numbers, no introductions.

Title: {title}
Description: {description}
Source: {source}
"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(GROQ_API_URL, json=payload, headers={
        "Authorization": GROQ_API_KEY,
        "Content-Type": "application/json"
    })

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]

        ideas = []
        for line in content.strip().split("\n"):
            line = re.sub(r"^\d+[\.\)]?\s*", "", line)
            line = re.sub(r"^[\.\-–•]+\s*", "", line)
            line = re.sub(r"(In this post|We (will )?discuss|This blog post (will )?)[:,]?\s*", "", line, flags=re.I)
            line = line.strip(" .:-\u2022")

            if len(line) > 10:
                ideas.append(line)

        return ideas

    return []


def score_and_prioritize_ideas(ideas, positive_keywords, negative_keywords):
    """
    Scores and ranks blog ideas based on:
    - Positive keyword relevance
    - Penalty for negative keyword presence
    - Uniqueness (number of distinct words)
    """
    scored = []

    for idea in ideas:
        idea_lower = idea.lower()
        matched_positive = [kw for kw in positive_keywords if kw.lower() in idea_lower]
        relevance = len(matched_positive)

        matched_negative = [kw for kw in negative_keywords if kw.lower() in idea_lower]
        penalty = len(matched_negative)

        words = idea_lower.split()
        unique_words = set(words)
        uniqueness = len(unique_words)

        score = relevance + uniqueness - penalty

        scored.append({
            "idea": idea,
            "score": score,
            "matched_positive": matched_positive,
            "matched_negative": matched_negative,
            "uniqueness": uniqueness
        })

    # Sort by descending score
    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    # ✅ Save to storage
    save_ideas(scored)

    return scored

# Blog Generator
This is an end-to-end content generation tool.. It automates everything from web research to writing and exporting full blog posts, all through a user-friendly Streamlit interface.<br>

## Project Structure

The project is organized into five focused Python files: <br>

scraper.py – Scrapes the web and filters content using spaCy, based on positive and negative keywords.<br>

ideagen.py – Generates blog ideas from the scraped articles and scores them.<br>

bloggeneration.py – Writes full blog content based on the highest-ranked idea.<br>

app.py – The Streamlit interface that allows users to interact with the system.<br>

storage.py – Saves outputs from all modules into a JSON file.<br>

## How It Works
### Web Scraping with spaCy <br>
To filter web content, I first used simple keyword matching (e.g., ignoring articles with negative terms). Then I added spaCy for more advanced features like: <br>

* Recognizing named entities <br>

* Matching keywords within those entities <br>

* Extracting noun phrases and entity types <br>

This makes it easy to enhance the system later, such as boosting relevance if a certain topic appears as an entity.
<br>

### Technical Topic Detection with Groq (LLaMA Model)
To decide when to use sources like Arxiv, I didn’t rely on a fixed list of keywords. Instead, I used Groq’s LLaMA model to classify topics as technical or non-technical using a short prompt. For example: <br>

“AI in education” → technical <br> 

“E-commerce in Algeria” → non-technical <br>

This helps avoid pulling in irrelevant results. <br>

### Idea Generation and Scoring
Groq is also used to generate blog ideas from each article. Each idea is then scored using three simple criteria:<br>

Relevance: Number of positive keywords found. <br>

Penalty: Number of negative keywords found.<br>

Uniqueness: Count of unique words in the idea title.<br>

Final score = relevance + uniqueness – penalty<br>

Ideas are stored with their scores, keyword matches, and word counts, and then ranked from highest to lowest.<br>

### Blog Writing and Export
Once a blog idea is selected, Groq writes the full article with:

* Headings <br>

* Bullet points <br>

* Examples <br>

* Markdown formatting <br>

The content is then converted into clean, styled PDFs using pdfkit.



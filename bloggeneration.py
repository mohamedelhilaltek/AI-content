# this module writes content based on the top 3 highest-scored ideas

import requests
import pdfkit
import re
import os
from storage import save_blog 

# API CONFIGURATION
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = f"Bearer {os.getenv('GROQ_API_KEY')}"
GROQ_MODEL = "llama3-70b-8192"


def generate_full_blog(idea_title):
    """
    Generates a full blog post using a given blog title prompt.
    """
    prompt = f"""Write a detailed, well-structured content based on the following title:

Title: {idea_title}

Make it informative, creative, and include headings, bullet points, and examples.
The output should be around 3 pages long, written in markdown-style formatting.
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
        blog_content = response.json()["choices"][0]["message"]["content"]

        # ✅ Save to storage
        save_blog(idea_title, {"title": idea_title, "content": blog_content})

        return blog_content

    return "❌ Error generating blog content."


def markdown_to_html(text):
    """
    Converts markdown-style text to clean HTML for PDF export.
    """
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)

    html_lines = []
    for line in text.split('\n'):
        line = line.strip()

        if not line:
            html_lines.append("<br>")
        elif line.startswith("<strong>") and line.endswith("</strong>"):
            html_lines.append(f"<h2>{line}</h2>")
        elif line.startswith("* "):
            html_lines.append(f"<li>{line[2:]}</li>")
        else:
            html_lines.append(f"<p>{line}</p>")

    return "\n".join(html_lines)


def save_blog_as_pdf(blog_content, filename="blog_post.pdf"):
    """
    Converts content into styled HTML and saves it as a PDF.
    """
    html_body = markdown_to_html(blog_content)

    html_content = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    font-size: 16px;
                    line-height: 1.6;
                }}
                h1 {{
                    font-size: 32px;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 40px;
                }}
                h2 {{
                    font-size: 24px;
                    font-weight: bold;
                    margin-top: 30px;
                    color: #2c3e50;
                }}
                p {{
                    margin-bottom: 15px;
                }}
                li {{
                    margin-left: 20px;
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <h1>Blog Post</h1>
            {html_body}
        </body>
    </html>
    """

    wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    pdfkit.from_string(html_content, filename, configuration=config)
    return filename

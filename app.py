
# this is an app used to enable the user interact with the ai agent 
import streamlit as st
from scraper import combine_search_results
from ideagen import generate_ideas_from_article, score_and_prioritize_ideas
from bloggeneration import generate_full_blog, save_blog_as_pdf
from urllib.parse import urlparse
import pandas as pd
import time

# Page Configuration
st.set_page_config(page_title="WeBetter AI Blog Generator", layout="wide")

# Sidebar with logo and app info
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Mohamed Elhilal</h3>", unsafe_allow_html=True)

# App Title
st.title("🧠 AI Content Generator")
st.markdown("Your personal AI assistant for generating SEO-optimized, idea-rich content.")

# Step 1: Keyword Input Section
st.markdown("## 🪄 Step 1: Enter Keywords")
col1, col2 = st.columns(2)
with col1:
    pos_keywords = st.text_input("✅ Positive Keywords (comma-separated)").split(",")
with col2:
    neg_keywords = st.text_input("❌ Negative Keywords (comma-separated)").split(",")

# Clean up keywords
pos_keywords = [kw.strip() for kw in pos_keywords if kw.strip()]
neg_keywords = [kw.strip() for kw in neg_keywords if kw.strip()]

# Step 2: Trigger Search & Generate Blog Ideas
if st.button("🔍 Search & Generate Ideas"):
    if not pos_keywords:
        st.error("⚠️ Please enter at least one positive keyword.")
    else:
        with st.spinner("🔎 Fetching articles from the web..."):
            query = " ".join(pos_keywords)
            articles = combine_search_results(query, pos_keywords, neg_keywords)
            st.session_state.articles = articles

        if not articles:
            st.error("❌ No articles found for your keywords. Try different ones.")
        else:
            st.success(f"✅ {len(articles)} articles found!")
            df = pd.DataFrame([{
                "Title": a["title"],
                "Description": a["description"],
                "Source": urlparse(a["link"]).netloc
            } for a in articles])
            st.dataframe(df)

            # Generate Blog Ideas from Articles
            st.markdown("## 💡 Step 2: Blog Title Ideas")
            all_ideas = []
            with st.spinner("💭 Generating Blog Ideas..."):
                for article in articles[:2]:  
                    ideas = generate_ideas_from_article(article["title"], article["description"], article["link"])
                    all_ideas.extend(ideas)
                    time.sleep(30)  # To respect Groq API rate limit

            prioritized = score_and_prioritize_ideas(all_ideas, pos_keywords, neg_keywords)
            st.session_state.prioritized_ideas = prioritized

            if prioritized:
                for i, item in enumerate(prioritized):
                    st.markdown(f"**{i + 1}.** {item['idea']} &nbsp;&nbsp;⭐ Score: `{item['score']}`")
            else:
                st.warning("No high-quality ideas generated. Try different keywords.")

# Step 3: Generate Full Blog Post Based on Top 3 Ideas
if "prioritized_ideas" in st.session_state and st.session_state.prioritized_ideas:
    st.markdown("## 📝 Step 3: Generate Full Blog Post")

    # Grab top 3 ideas
    top_ideas = st.session_state.prioritized_ideas[:3]

    # Show the ideas being used
    st.markdown("### 🔥 Using Top 3 Ranked Ideas:")
    for i, item in enumerate(top_ideas):
        st.markdown(f"**{i+1}.** {item['idea']}  ⭐ Score: `{item['score']}`")

    if st.button("✍️ Generate Blog from Top 3 Ideas"):
        with st.spinner("🛠️ Generating a comprehensive blog post..."):
            # Combine ideas into a single prompt
            prompt = "Write a detailed, well-structured blog post that combines the following ideas:\n\n"
            for idea in top_ideas:
                prompt += f"- {idea['idea']}\n"
            prompt += "\nMake sure the post flows naturally, includes examples, and uses headings where needed."

            # Generate blog using Groq
            blog = generate_full_blog(prompt)
            st.session_state.blog_content = blog

        if "blog_content" in st.session_state:
            st.success("🎉 Comprehensive blog post generated!")
            st.markdown("## 📄 Blog Preview")
            st.write(st.session_state.blog_content)

            # PDF Download Button
            pdf_file = save_blog_as_pdf(st.session_state.blog_content)
            with open(pdf_file, "rb") as f:
                st.download_button(
                    "📥 Download PDF",
                    f,
                    file_name="generated_blog.pdf",
                    mime="application/pdf"
                )
import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

# 🔐 Set your Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama3-70b-8192"

# 🌐 Hardcoded website URL
STATIC_WEBSITE_URL = "https://shaukatkhanum.org.pk/"  # 🔁 Change this to your target site

# 📄 Extract and clean website content
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        text = ' '.join(soup.stripped_strings)
        return text[:4000]
    except Exception as e:
        return f"Error fetching content: {e}"

# 🤖 Query Groq API
def query_groq(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                 headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error querying Groq: {e}"

# 🕒 Cache website content and auto-refresh every 3 hours (10800s)
@st.cache_data(ttl=10800, show_spinner=False)
def get_static_site_content():
    return extract_text_from_url(STATIC_WEBSITE_URL)

# 🚀 Streamlit UI
st.set_page_config(page_title="Static Website Chatbot", layout="centered")
st.title("💬 Website Chatbot using Groq")
st.markdown(f"**Target website:** `{STATIC_WEBSITE_URL}`")

# 🔁 Manual refresh
if st.button("🔄 Refresh Website Content Now"):
    st.cache_data.clear()
    st.success("Website content will be refreshed on next question.")

# ❓ Ask questions
question = st.text_area("Ask a question about the website:", height=100)

if st.button("Ask"):
    if not GROQ_API_KEY:
        st.error("❌ Missing Groq API Key. Set it via environment variable or Streamlit secrets.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            context = get_static_site_content()
            if context.startswith("Error"):
                st.error(context)
            else:
                prompt = f"The following is content from the website:\n\n{context}\n\nQuestion: {question}\nAnswer:"
                answer = query_groq(prompt)
                st.success("✅ Answer:")
                st.write(answer)

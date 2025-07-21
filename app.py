import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

# 🔐 Groq API Key setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama3-70b-8192"

# 🌐 Hardcoded Website URL
STATIC_WEBSITE_URL = "https://shaukatkhanum.org.pk/"  # ← Replace with your real site

# 🧹 Extract website text
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        text = ' '.join(soup.stripped_strings)
        return text[:4000]
    except Exception as e:
        return f"Error: {e}"

# 🧠 Query Groq API
def query_groq(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error from Groq API: {e}"

# 🔁 Auto-refresh website content every 3 hours
@st.cache_data(ttl=10800)
def get_static_site_content():
    return extract_text_from_url(STATIC_WEBSITE_URL)

# 🎨 CSS for floating chatbot
st.markdown("""
    <style>
    .chatbox {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        max-height: 600px;
        background-color: #f9f9f9;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        padding: 15px;
        z-index: 9999;
        overflow-y: auto;
    }
    .chatbox h4 {
        margin-top: 0;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 🧱 Layout using HTML
st.markdown('<div class="chatbox">', unsafe_allow_html=True)
st.markdown("### 🤖 Website Chatbot")

st.markdown(f"<sub>Site: <i>{STATIC_WEBSITE_URL}</i></sub>", unsafe_allow_html=True)

# 🔁 Manual refresh button
if st.button("🔄 Refresh Site Content"):
    st.cache_data.clear()
    st.info("Website content will refresh on next message.")

# Chat input
question = st.text_input("Ask something about the website:")

if question and st.button("Ask"):
    if not GROQ_API_KEY:
        st.error("Groq API Key is missing. Set it using environment variable or secrets.")
    else:
        with st.spinner("Thinking..."):
            context = get_static_site_content()
            if context.startswith("Error"):
                st.error(context)
            else:
                prompt = f"The following is the content of the website:\n\n{context}\n\nQuestion: {question}\nAnswer:"
                answer = query_groq(prompt)
                st.success("Answer:")
                st.markdown(answer)

st.markdown('</div>', unsafe_allow_html=True)

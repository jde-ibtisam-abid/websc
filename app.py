import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

# --- Configure the page ---
st.set_page_config(page_title="Chatbot Widget", layout="centered", page_icon="💬")
# Inject CSS to mimic a small chatbot widget for iframe use.
st.markdown("""
    <style>
      /* Remove padding and set a maximum width so the widget stays compact */
      .reportview-container .main .block-container {
          padding: 0rem;
          max-width: 320px;
      }
      body {
          background-color: transparent;
      }
    </style>
    """, unsafe_allow_html=True)

# --- Hardcoded Website Settings ---
STATIC_WEBSITE_URL = "https://shaukatkhanum.org.pk/"  # Replace with your target website

# --- Groq API Settings ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama3-70b-8192"  # Change to your preferred Groq-supported model if needed

# --- Function to scrape and clean website content ---
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        text = ' '.join(soup.stripped_strings)
        return text[:4000]  # Trim to limit prompt size
    except Exception as e:
        return f"Error fetching content: {e}"

# --- Function to query the Groq API ---
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

# --- Cache website content and auto-refresh every 3 hours (10800 seconds) ---
@st.cache_data(ttl=10800, show_spinner=False)
def get_static_site_content():
    return extract_text_from_url(STATIC_WEBSITE_URL)

# --- Chat Widget UI ---
st.markdown("### 💬 Chatbot")
st.markdown(f"**Website:** `{STATIC_WEBSITE_URL}`")

# Input field for asking a question about the website
question = st.text_input("Ask a question about the website:")

if st.button("Send"):
    if not GROQ_API_KEY:
        st.error("Missing Groq API Key. Please set it via an environment variable or in Streamlit secrets.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            context = get_static_site_content()
            if context.startswith("Error"):
                st.error(context)
            else:
                prompt = f"Content from the website:\n\n{context}\n\nQuestion: {question}\nAnswer:"
                answer = query_groq(prompt)
                st.markdown("**Answer:**")
                st.write(answer)

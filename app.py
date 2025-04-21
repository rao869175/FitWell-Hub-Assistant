import os

# Install required libraries
os.system("pip install beautifulsoup4")
os.system("pip install googletrans==4.0.0-rc1")

import requests
import streamlit as st
from bs4 import BeautifulSoup
from googletrans import Translator

# Initialize Translator
translator = Translator()

# Set your Groq API key and API URL
GROQ_API_KEY = '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'
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'

# Function to scrape website content without altering it
def scrape_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the full body of the page and extract everything as text
        body_content = soup.find('body')
        if body_content:
            content = body_content.get_text(separator=" ", strip=True)
        else:
            content = "Error: Unable to find body content on the page."

        return content
    except Exception as e:
        return f"Error scraping {url}: {e}"

# Scrape content from websites
fitwellhub_pk_content = scrape_website('https://fitwellhub.pk/')
fitwellhub_com_content = scrape_website('https://fitwellhub.com/')
ss_group_content = scrape_website('https://www.ssgroup.pk/')

# Combine all content
combined_content = f"{fitwellhub_pk_content}\n{fitwellhub_com_content}\n{ss_group_content}"

# Function to call Groq API
def call_groq_api(prompt):
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Answer accurately based on the provided website information."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    else:
        return f"Error from Groq API: {response.text}"

# Streamlit interface layout
st.title("🩺 FitWell Hub Assistant")
st.write("""
   Hi! I am FitWell Hub Assistant. How can I help you today?
""")

# User input field
user_input = st.text_input("Ask a question about FitWell Hub:", placeholder="Type your question here...")

# Send button
if st.button("Send"):
    if user_input.strip() == "":
        st.warning("Please type a question before sending.")
    else:
        # Detect language
        detected_lang = translator.detect(user_input)
        if detected_lang.lang != 'en':
            user_input_en = translator.translate(user_input, src=detected_lang.lang, dest='en').text
        else:
            user_input_en = user_input

        # Check for developer-related questions
        if any(kw in user_input_en.lower() for kw in ["developer", "who made you", "your developer name", "created you", "who is your developer"]):
            answer_en = "My developer name is Rao Zain."
        else:
            # Build prompt for Groq API
            prompt = f"Based on the following information:\n{combined_content}\n\nAnswer the question: {user_input_en}"

            try:
                answer_en = call_groq_api(prompt)
            except Exception as e:
                answer_en = f"Error generating response: {e}"

        # Translate back if needed
        if detected_lang.lang != 'en':
            response = translator.translate(answer_en, src='en', dest=detected_lang.lang).text
        else:
            response = answer_en

        # Display assistant's response
        st.markdown(f"""
        <div style="background-color:white; padding: 15px; border-radius: 8px; color:#333; font-size: 16px;">
            <strong>FitWell Hub Assistant:</strong> {response}
        </div>
        """, unsafe_allow_html=True)

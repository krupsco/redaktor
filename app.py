import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Wczytanie klucza API z .env lub sekretów Streamlit Cloud
load_dotenv()

# Inicjalizacja klienta OpenAI (klucz pobierany automatycznie z OPENAI_API_KEY)
client = OpenAI()

def load_prompt(platform: str) -> str:
    try:
        with open(f"prompts/{platform}.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def generate_output(user_text: str, rules: str) -> str:
    prompt = f"""
Zasady redakcyjne dla tej platformy:
{rules}

Tekst do redakcji:
{user_text}

Wygeneruj gotowy tekst zgodny z powyższymi zasadami.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

st.set_page_config(page_title="Redaktor AI", layout="centered")
st.title("📝 Redaktor AI")

platform = st.selectbox("Wybierz platformę docelową", ["facebook", "instagram", "newsletter"])
user_text = st.text_area("Wklej surowy tekst lub notatkę:")

if st.button("Zredaguj tekst"):
    if not user_text.strip():
        st.warning("Proszę wprowadzić tekst do redakcji.")
    else:
        rules = load_prompt(platform)
        if not rules:
            st.error(f"Brak zasad redakcyjnych dla platformy '{platform}'.")
        else:
            with st.spinner("Redaguję tekst..."):
                output = generate_output(user_text, rules)
                st.success("Gotowy tekst:")
                st.text_area("Wynik:", value=output, height=300)

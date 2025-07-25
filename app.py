import streamlit as st
import os
from openai import OpenAI

# Inicjalizacja klienta OpenAI z sekretem
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Funkcja pomocnicza do wczytania głównego promptu z pliku
@st.cache_data
def load_main_prompt():
    try:
        with open("prompt_base.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# Funkcja do generowania posta
def generate_output(user_text: str, tone_level: int, use_emojis: bool, temperature: float, char_limit: int, post_type: str) -> str:
    type_instruction = {
        "Wydarzenie": "Skup się na zaproszeniu na wydarzenie. Podkreśl datę, miejsce i dlaczego warto wziąć udział.",
        "Sprzedażowy": "Skup się na zachęcie do zakupu, uczestnictwa lub skorzystania z oferty. Użyj języka korzyści.",
        "Okazjonalny": "To post okolicznościowy. Podkreśl emocje, wyjątkowość chwili lub rocznicę, nie zapomnij o kontekście kulturowym lub historycznym."
    }[post_type]

    base_prompt = load_main_prompt()

    full_prompt = f"""
{base_prompt}

---
Tekst do redakcji:
{user_text}
---

Wymagania dodatkowe:
- Poziom powagi posta (1–10): {tone_level}
- Czy używać emotikonek: {"tak" if use_emojis else "nie"}
- Typ posta: {post_type}
- {type_instruction}

Długość posta: do {char_limit} znaków.  
Format: 2–4 akapity.  
Platformy docelowe: Facebook, Instagram.

Wygeneruj gotowy tekst zgodny z powyższymi zasadami.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd API: {e}"

# --------------------------
# INTERFEJS STREAMLIT
# --------------------------

st.set_page_config(page_title="Redaktor AI", layout="centered")
st.title("Zamkowy Redaktor SM")

# Inicjalizacja zmiennych sesji
if 'output_text' not in st.session_state:
    st.session_state.output_text = ""
if 'finalized' not in st.session_state:
    st.session_state.finalized = False
if 'refresh_key' not in st.session_state:
    st.session_state.refresh_key = 0

# Dane wejściowe
user_text = st.text_area("Wklej surowy tekst lub notatkę:")

post_type = st.radio("Jaki to rodzaj posta?", ["Wydarzenie", "Sprzedażowy", "Okazjonalny"])
char_limit = st.selectbox("Maksymalna długość posta:", [500, 1000, 1500])
tone_level = st.slider("Jak poważny ma być post?", min_value=1, max_value=10, value=5)
use_emojis = st.checkbox("Użyć emotikonek w poście?")
creativity = st.slider("Kreatywność (temperatura)", min_value=1, max_value=10, value=7)
temperature = creativity / 10

# Generowanie nowego tekstu
if st.button("Zredaguj tekst"):
    if not user_text.strip():
        st.warning("Proszę wprowadzić tekst do redakcji.")
    else:
        with st.spinner("Redaguję tekst..."):
            output = generate_output(user_text, tone_level, use_emojis, temperature, char_limit, post_type)
            st.session_state.output_text = output
            st.session_state.finalized = False
            # Zresetuj klucz odświeżania, by wymusić przeładowanie pola
            st.session_state.refresh_key += 1

# Wyświetlanie wygenerowanego tekstu i możliwość edycji
if st.session_state.output_text:
    st.success("Gotowy tekst:")
    edited_text = st.text_area(
        "Wynik:", 
        value=st.session_state.output_text, 
        height=300, 
        key=f"generated_text_{st.session_state.refresh_key}"
    )
    st.session_state.output_text = edited_text  # aktualizacja tekstu jeśli użytkownik ręcznie zmieni

    if not st.session_state.finalized:
        feedback = st.text_area("Czy chcesz dodać poprawki redakcyjne? Opisz je tutaj:", key="feedback")

        if st.button("Uwzględnij poprawki") and feedback.strip():
            with st.spinner("Wprowadzam poprawki..."):
                try:
                    instruction = f"Uwzględnij poniższe poprawki do wygenerowanego posta:\n{feedback}"
                    revised_response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "Jesteś redaktorem mediów społecznościowych."},
                            {"role": "user", "content": st.session_state.output_text},
                            {"role": "user", "content": instruction}
                        ],
                        temperature=temperature,
                    )
                    st.session_state.output_text = revised_response.choices[0].message.content
                    st.session_state.finalized = False
                    st.success("Poprawki uwzględnione.")
                    # Zwiększ klucz odświeżania, by wymusić odświeżenie pola tekstowego
                    st.session_state.refresh_key += 1
                except Exception as e:
                    st.error(f"Błąd API: {e}")

    # Przycisk do ręcznego odświeżenia pola z tekstem (np. gdy edycja się nie pokazuje)
    if st.button("Pokaż poprawki"):
        st.session_state.refresh_key += 1

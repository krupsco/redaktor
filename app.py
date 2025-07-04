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
Jesteś redaktorem mediów społecznościowych Zamku Królewskiego w Warszawie. Twoim zadaniem jest tworzenie angażujących postów w stylu tej instytucji – łącząc kulturę, historię, edukację i emocje.

Na podstawie poniższych informacji (opis wydarzenia, temat, kontekst), stwórz post na Facebooka i/lub Instagram:

---
Tekst do redakcji:
{user_text}
---

Wymagania:

1. **Styl i ton wypowiedzi:**
   - Półformalny, przystępny, elegancki, z emocjonalnym zaangażowaniem.
   - Używaj pierwszej osoby liczby mnogiej („Cieszymy się…”, „Zapraszamy…”).
   - Dodaj nutkę zachwytu, dumy lub ciekawości – bez patosu.
   - Możesz użyć lekkiego humoru lub pytania do odbiorców.

2. **Struktura posta:**
   - **Akapit 1:** Emocjonalne wprowadzenie – kontekst, atmosfera, cel posta.
   - **Akapit 2–3:** Opis szczegółowy – co, kto, gdzie, dlaczego to ważne.
   - **Akapit końcowy:** Wezwanie do działania lub zachęta do udziału/zainteresowania. Możesz też dodać ciekawostkę lub pytanie.

3. **Język i słownictwo:**
   - Wpleć słownictwo typowe dla kultury i historii (np. „dziedzictwo”, „kolekcja”, „scenografia”, „emocje”, „dzieło”).
   - Nie używaj skrótów młodzieżowych; możesz dodać 1–2 pasujące emoji.
   - Dopuszczalne słownictwo specjalistyczne, ale tylko w zrozumiałym kontekście.

4. **Wzmianki:**
   - Jeśli obecne są partnerzy, autorzy, goście – wymień ich z imienia i nazwiska.
   - Jeśli dotyczy wydarzenia na Zamku – wspomnij o jego lokalizacji.
   - Jeśli to zaproszenie – dodaj informację o dacie, miejscu lub link.

Długość posta: do 1000 znaków.  
Format: 2–4 akapity.  
Platformy docelowe: Facebook, Instagram.



Wygeneruj gotowy tekst zgodny z powyższymi zasadami.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd API: {e}"


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

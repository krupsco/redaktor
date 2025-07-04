import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Wczytaj klucz API
load_dotenv()
client = OpenAI()

# Funkcja główna
def generate_output(user_text: str, tone_level: int, use_emojis: bool, temperature: float, char_limit: int, post_type: str) -> str:
    # Instrukcja zależna od typu posta
    if post_type == "Wydarzenie":
        type_instruction = "Skup się na zaproszeniu na wydarzenie. Podkreśl datę, miejsce i dlaczego warto wziąć udział."
    elif post_type == "Sprzedażowy":
        type_instruction = "Skup się na zachęcie do zakupu, uczestnictwa lub skorzystania z oferty. Użyj języka korzyści."
    elif post_type == "Okazjonalny":
        type_instruction = "To post okolicznościowy. Podkreśl emocje, wyjątkowość chwili lub rocznicę, nie zapomnij o kontekście kulturowym lub historycznym."

    prompt = f"""
Jesteś redaktorem mediów społecznościowych Zamku Królewskiego w Warszawie. Twoim zadaniem jest tworzenie angażujących postów w stylu tej instytucji – łącząc kulturę, historię, edukację i emocje.

Na podstawie poniższych informacji (opis wydarzenia, temat, kontekst), stwórz post na Facebooka i/lub Instagram:

---
Tekst do redakcji:
{user_text}
---

Wymagania dodatkowe:
- Poziom powagi posta (1–10): {tone_level}
- Czy używać emotikonek: {"tak" if use_emojis else "nie"}
- Typ posta: {post_type}
- {type_instruction}

Zasady:

1. **Styl i ton wypowiedzi:**
   - Półformalny, przystępny, elegancki, z emocjonalnym zaangażowaniem – dostosuj powagę wypowiedzi do poziomu {tone_level}/10.
   - Używaj pierwszej osoby liczby mnogiej („Cieszymy się…”, „Zapraszamy…”).
   - Dodaj nutkę zachwytu, dumy lub ciekawości – bez patosu.
   - {"Możesz dodać 1–2 pasujące emoji." if use_emojis else "Nie używaj emotikonek."}
   - Możesz użyć lekkiego humoru lub pytania do odbiorców.

2. **Struktura posta:**
   - **Akapit 1:** Emocjonalne wprowadzenie – kontekst, atmosfera, cel posta.
   - **Akapit 2–3:** Opis szczegółowy – co, kto, gdzie, dlaczego to ważne.
   - **Akapit końcowy:** Wezwanie do działania lub ciekawostka.

3. **Język i słownictwo:**
   - Wpleć słownictwo typowe dla kultury i historii (np. „dziedzictwo”, „kolekcja”, „scenografia”, „emocje”, „dzieło”).
   - Unikaj skrótów młodzieżowych.
   - Dopuszczalne słownictwo specjalistyczne, ale tylko w zrozumiałym kontekście.

4. **Wzmianki:**
   - Jeśli obecne są partnerzy, autorzy, goście – wymień ich z imienia i nazwiska.
   - Jeśli dotyczy wydarzenia na Zamku – wspomnij o jego lokalizacji.
   - Jeśli to zaproszenie – dodaj informację o dacie, miejscu lub link.

Długość posta: do {char_limit} znaków.  
Format: 2–4 akapity.  
Platformy docelowe: Facebook, Instagram.

Wygeneruj gotowy tekst zgodny z powyższymi zasadami.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
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

# Główne dane wejściowe
user_text = st.text_area("Wklej surowy tekst lub notatkę:")

# Nowe opcje: typ posta i długość
post_type = st.radio("Jaki to rodzaj posta?", ["Wydarzenie", "Sprzedażowy", "Okazjonalny"])
char_limit = st.selectbox("Maksymalna długość posta:", [500, 1000, 1500])

# Istniejące opcje: ton, emoji, kreatywność
tone_level = st.slider("Jak poważny ma być post?", min_value=1, max_value=10, value=5)
use_emojis = st.checkbox("Użyć emotikonek w poście?")
creativity = st.slider("Kreatywność (temperatura)", min_value=1, max_value=10, value=7)
temperature = creativity / 10  # konwersja na wartość od 0.1 do 1.0

# Generowanie posta
if st.button("Zredaguj tekst"):
    if not user_text.strip():
        st.warning("Proszę wprowadzić tekst do redakcji.")
    else:
        with st.spinner("Redaguję tekst..."):
            output = generate_output(user_text, tone_level, use_emojis, temperature, char_limit, post_type)
            st.success("Gotowy tekst:")
            st.text_area("Wynik:", value=output, height=300)

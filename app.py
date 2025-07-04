def generate_output(user_text: str, tone_level: int, use_emojis: bool, temperature: float, char_limit: int, post_type: str) -> str:
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
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        result = response.choices[0].message.content
        log_prompt_and_result(prompt, result)  # <-- Zapisz do logu
        return result
    except Exception as e:
        return f"Błąd API: {e}"

import streamlit as st
import pandas as pd

# 1. NYELVI SZÓTÁR LÉTREHOZÁSA
translations = {
    "hu": {
        "title": "🚗 Professzionális Alkatrész Adatbázis",
        "sidebar_header": "Keresési feltételek",
        "brand_select": "Márka kiválasztása",
        "year_range": "Évjárat intervallum",
        "cat_select": "Kategória",
        "search_label": "Kulcsszó kereső (pl. hangszóró)",
        "results_count": "Talált modellek száma",
        "download_btn": "Lista letöltése CSV-ben",
        "no_results": "Nincs találat a megadott szűrőkkel.",
        "cats": ["Futómű", "Motor", "Elektronika", "Beltér", "Kültér", "Kaszni"],
        "part_gen": "specifikus Hangszóró / Kábelköteg"
    },
    "en": {
        "title": "🚗 Professional Auto Parts Database",
        "sidebar_header": "Search Filters",
        "brand_select": "Select Brand",
        "year_range": "Year Range",
        "cat_select": "Category",
        "search_label": "Keyword search (e.g. speaker)",
        "results_count": "Number of models found",
        "download_btn": "Download list in CSV",
        "no_results": "No results found with the given filters.",
        "cats": ["Suspension", "Engine", "Electronics", "Interior", "Exterior", "Body"],
        "part_gen": "specific Speaker / Wiring harness"
    }
}

# 2. ADATOK BETÖLTÉSE (NYÍLT FORRÁSBÓL)
@st.cache_data
def load_real_data():
    # Nyílt autóadatbázis linkje
    url = "https://githubusercontent.com"
    try:
        raw_df = pd.read_csv(url)
        df = raw_df[['make', 'model', 'year']].copy()
        df.columns = ['Márka', 'Modell', 'Év']
        # Megtisztítjuk az éveket, hogy biztosan számok legyenek
        df['Év'] = pd.to_numeric(df['Év'], errors='coerce')
        df = df.dropna(subset=['Év'])
        return df
    except:
        # Ha a link nem érhető el, egy vészhelyzeti kis táblázat
        return pd.DataFrame({
            'Márka': ['Audi', 'BMW', 'Volkswagen'],
            'Modell': ['A4', '320d', 'Golf'],
            'Év': [2020, 2018, 2015]
        })

df = load_real_data()

# 3. UI BEÁLLÍTÁSOK ÉS NYELVVÁLASZTÓ
st.set_page_config(page_title="Auto Parts UI", layout="wide")

# Nyelvválasztó sáv
lang_col1, lang_col2 = st.columns([4, 1])
with lang_col2:
    lang = st.radio("Language / Nyelv", options=["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    lang_code = "hu" if "🇭🇺" in lang else "en"

t = translations[lang_code]

# 4. OLDAL MEGJELENÍTÉSE
st.title(t["title"])
st.sidebar.header(t["sidebar_header"])

# --- SZŰRŐK ---
# Márka szűrő
available_brands = sorted(df['Márka'].unique())
brand_selection = st.sidebar.multiselect(t["brand_select"], options=available_brands, default=["Audi", "BMW", "Volkswagen"][:len(available_brands)])

# Évszám szűrő (JAVÍTOTT VERZIÓ)
min_db_year = int(df['Év'].min())
max_db_year = int(df['Év'].max())
year_range = st.sidebar.slider(
    t["year_range"], 
    min_db_year, 
    max_db_year, 
    (max(2010, min_db_year), min(2023, max_db_year))
)

# Kategória szűrő
cat_selection = st.sidebar.multiselect(t["cat_select"], options=t["cats"], default=[t["cats"][2]]) # Alapértelmezett: Elektronika

# Szöveges kereső
search_term = st.sidebar.text_input(t["search_label"], "")

# 5. SZŰRÉSI FOLYAMAT
filtered_df = df[
    (df['Márka'].isin(brand_selection)) & 
    (df['Év'].between(year_range[0], year_range[1]))
].copy()

# Alkatrész adatok generálása a választott nyelven
if not filtered_df.empty:
    selected_cats_str = ", ".join(cat_selection) if cat_selection else "N/A"
    filtered_df['Kategória'] = selected_cats_str
    filtered_df['Alkatrész'] = filtered_df['Márka'] + " " + t["part_gen"]
    
    # Keresés szűkítése
    if search_term:
        filtered_df = filtered_df[filtered_df['Alkatrész'].str.contains(search_term, case=False)]

# 6. EREDMÉNYEK KIÍRÁSA
st.metric(t["results_count"], len(filtered_df))
st.dataframe(filtered_df, use_container_width=True)

# Letöltés gomb
if not filtered_df.empty:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(t["download_btn"], data=csv, file_name="parts_list.csv", mime="text/csv")
else:
    st.warning(t["no_results"])

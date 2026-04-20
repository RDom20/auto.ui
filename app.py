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

# 2. ADATOK BETÖLTÉSE (MARAD A RÉGI FORRÁS)
@st.cache_data
def load_real_data():
    url = "https://githubusercontent.com"
    try:
        raw_df = pd.read_csv(url)
        df = raw_df[['make', 'model', 'year']].copy()
        df.columns = ['Márka', 'Modell', 'Év']
        return df
    except:
        return pd.DataFrame(columns=['Márka', 'Modell', 'Év'])

df = load_real_data()

# 3. NYELVVÁLASZTÓ UI (Zászlókkal)
st.set_page_config(page_title="Auto Parts DB", layout="wide")

# Nyelvválasztó a jobb felső sarokban
col1, col2 = st.columns([8, 2])
with col2:
    lang = st.radio("Language / Nyelv", options=["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    lang_code = "hu" if "🇭🇺" in lang else "en"

t = translations[lang_code]

# 4. UI MEGJELENÍTÉSE A VÁLASZTOTT NYELVEN
st.title(t["title"])
st.sidebar.header(t["sidebar_header"])

available_brands = sorted(df['Márka'].unique())
brand_selection = st.sidebar.multiselect(t["brand_select"], options=available_brands, default=["Audi", "BMW"] if "Audi" in available_brands else None)

year_range = st.sidebar.slider(t["year_range"], int(df['Év'].min()), int(df['Év'].max()), (2010, 2023))

cat_selection = st.sidebar.multiselect(t["cat_select"], options=t["cats"], default=[t["cats"][2]]) # Alapértelmezett: Elektronika

search_term = st.sidebar.text_input(t["search_label"], "")

# 5. SZŰRÉS ÉS MEGJELENÍTÉS
filtered_df = df[(df['Márka'].isin(brand_selection)) & (df['Év'].between(year_range[0], year_range[1]))].copy()

# Alkatrészek generálása a választott nyelven
filtered_df['Kategória'] = ", ".join(cat_selection) if cat_selection else "N/A"
filtered_df['Alkatrész'] = filtered_df['Márka'] + " " + t["part_gen"]

if search_term:
    filtered_df = filtered_df[filtered_df['Alkatrész'].str.contains(search_term, case=False)]

st.metric(t["results_count"], len(filtered_df))
st.dataframe(filtered_df, use_container_width=True)

if not filtered_df.empty:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(t["download_btn"], data=csv, file_name="parts.csv", mime="text/csv")
else:
    st.warning(t["no_results"])

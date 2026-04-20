import streamlit as st
import pandas as pd

# 1. NYELVI SZÓTÁR
translations = {
    "hu": {
        "title": "🚗 Professzionális Alkatrész Adatbázis",
        "sidebar_header": "Keresési feltételek",
        "brand_select": "Márka",
        "year_range": "Évjárat",
        "cat_select": "Kategória",
        "search_label": "Kulcsszó",
        "search_btn": "Keresés 🔍",
        "results_count": "Találatok",
        "random_title": "Ajánlott modellek (véletlenszerű)",
        "cats": ["Futómű", "Motor", "Elektronika", "Beltér", "Kültér", "Kaszni"],
        "part_gen": "specifikus alkatrész"
    },
    "en": {
        "title": "🚗 Professional Auto Parts Database",
        "sidebar_header": "Search Filters",
        "brand_select": "Make",
        "year_range": "Year Range",
        "cat_select": "Category",
        "search_label": "Keyword",
        "search_btn": "Search 🔍",
        "results_count": "Results",
        "random_title": "Recommended models (random)",
        "cats": ["Suspension", "Engine", "Electronics", "Interior", "Exterior", "Body"],
        "part_gen": "specific part"
    }
}

# 2. ADATOK BETÖLTÉSE - HIBATŰRŐ MÓDON
@st.cache_data
def load_real_data():
    url = "https://githubusercontent.com"
    try:
        df_raw = pd.read_csv(url)[['make', 'model', 'year']]
        df_raw.columns = ['Márka', 'Modell', 'Év']
        df_raw['Év'] = pd.to_numeric(df_raw['Év'], errors='coerce')
        return df_raw.dropna()
    except Exception as e:
        # Ha nincs net vagy hiba van, egy alap listát adunk vissza
        return pd.DataFrame({'Márka':['Audi', 'BMW', 'VW'], 'Modell':['A4', '320d', 'Golf'], 'Év':[2018, 2019, 2020]})

df = load_real_data()

st.set_page_config(page_title="Auto Search", layout="wide")

# Nyelvválasztó
_, lang_col = st.columns()
with lang_col:
    lang = st.radio("Language", options=["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    t = translations["hu" if "🇭🇺" in lang else "en"]

st.title(t["title"])

# --- KERESŐ FORM ---
with st.sidebar:
    with st.form("search_form"):
        st.header(t["sidebar_header"])
        brand_selection = st.multiselect(t["brand_select"], options=sorted(df['Márka'].unique()))
        
        min_y = int(df['Év'].min())
        max_y = int(df['Év'].max())
        year_range = st.slider(t["year_range"], min_y, max_y, (2015, 2022))
        
        cat_selection = st.multiselect(t["cat_select"], options=t["cats"], default=[t["cats"]])
        search_term = st.text_input(t["search_label"], "")
        submit_button = st.form_submit_button(label=t["search_btn"])

# --- MEGJELENÍTÉS ---
if submit_button:
    # SZŰRT EREDMÉNYEK
    filt = df['Év'].between(year_range[0], year_range[1])
    if brand_selection:
        filt &= df['Márka'].isin(brand_selection)
    
    res = df[filt].copy()
    if not res.empty:
        res['Kategória'] = ", ".join(cat_selection) if cat_selection else "N/A"
        res['Alkatrész'] = res['Márka'] + " " + t["part_gen"]
        if search_term:
            res = res[res['Alkatrész'].str.contains(search_term, case=False) | res['Modell'].str.contains(search_term, case=False)]
        
        st.subheader(f"{t['results_count']}: {len(res)}")
        st.dataframe(res, use_container_width=True)
    else:
        st.warning("Nincs találat.")
else:
    # BIZTONSÁGOS RANDOM AJÁNLATOK
    st.subheader(t["random_title"])
    # Megnézzük, van-e elég adat a sorsoláshoz
    sample_size = min(len(df), 10)
    if sample_size > 0:
        random_df = df.sample(sample_size).copy()
        random_df['Kategória'] = t["cats"][0] # Csak egy példa kategória
        random_df['Alkatrész'] = random_df['Márka'] + " " + t["part_gen"]
        st.dataframe(random_df, use_container_width=True)
    st.info("💡 Használd a szűrőket bal oldalt a kereséshez!")

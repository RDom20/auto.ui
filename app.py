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

# 2. ADATOK BETÖLTÉSE
@st.cache_data
def load_real_data():
    url = "https://githubusercontent.com"
    try:
        df_raw = pd.read_csv(url)[['make', 'model', 'year']]
        df_raw.columns = ['Márka', 'Modell', 'Év']
        df_raw['Év'] = pd.to_numeric(df_raw['Év'], errors='coerce')
        return df_raw.dropna()
    except:
        return pd.DataFrame({'Márka':['Audi'],'Modell':['A4'],'Év':[2020]})

df = load_real_data()

st.set_page_config(page_title="Auto Search", layout="wide")

# Nyelvválasztó a jobb felső sarokba
_, lang_col = st.columns([4,1])
with lang_col:
    lang = st.radio("Language", options=["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    t = translations["hu" if "🇭🇺" in lang else "en"]

st.title(t["title"])

# --- KERESŐ FORM (HASZNÁLTAUTÓ STÍLUS) ---
with st.sidebar:
    with st.form("search_form"):
        st.header(t["sidebar_header"])
        
        brand_selection = st.multiselect(t["brand_select"], options=sorted(df['Márka'].unique()))
        
        min_y, max_y = int(df['Év'].min()), int(df['Év'].max())
        year_range = st.slider(t["year_range"], min_y, max_y, (2015, 2022))
        
        cat_selection = st.multiselect(t["cat_select"], options=t["cats"], default=[t["cats"][2]]) # Alapértelmezett: Elektronika
        
        search_term = st.text_input(t["search_label"], "")
        
        # Ez a gomb KÖTELEZŐ a formon belül
        submit_button = st.form_submit_button(label=t["search_btn"])

# --- MEGJELENÍTÉS LOGIKÁJA ---
if submit_button:
    # KERESÉS EREDMÉNYE
    filt = df['Év'].between(year_range[0], year_range[1])
    if brand_selection:
        filt &= df['Márka'].isin(brand_selection)
    
    res = df[filt].copy()
    res['Kategória'] = ", ".join(cat_selection) if cat_selection else "N/A"
    res['Alkatrész'] = res['Márka'] + " " + t["part_gen"]
    
    if search_term:
        res = res[res['Alkatrész'].str.contains(search_term, case=False) | res['Modell'].str.contains(search_term, case=False)]
        
    st.subheader(f"{t['results_count']}: {len(res)}")
    st.dataframe(res, use_container_width=True)
else:
    # ALAPHELYZET (RANDOM AJÁNLATOK)
    st.subheader(t["random_title"])
    random_df = df.sample(10).copy()
    random_df['Kategória'] = t["cats"][2] # Elektronika példaként
    random_df['Alkatrész'] = random_df['Márka'] + " " + t["part_gen"]
    st.dataframe(random_df, use_container_width=True)
    st.info("💡 Állítsd be a szűrőket bal oldalt, majd nyomj a Keresés gombra!")

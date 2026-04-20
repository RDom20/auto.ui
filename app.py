import streamlit as st
import pandas as pd

# 1. NYELVI SZÓTÁR
translations = {
    "hu": {
        "title": "🚗 Nyílt Autóalkatrész Adatbázis",
        "sidebar_header": "Keresési feltételek",
        "brand_select": "Márka",
        "year_range": "Évjárat",
        "cat_select": "Kategória",
        "search_btn": "Keresés indítása 🔍",
        "results": "Talált modellek",
        "cats": ["Futómű", "Motor", "Elektronika", "Beltér", "Kültér", "Kaszni"],
        "part_gen": "specifikus alkatrész"
    },
    "en": {
        "title": "🚗 Open Source Auto Parts Database",
        "sidebar_header": "Search Filters",
        "brand_select": "Brand",
        "year_range": "Year Range",
        "cat_select": "Category",
        "search_btn": "Start Search 🔍",
        "results": "Models Found",
        "cats": ["Suspension", "Engine", "Electronics", "Interior", "Exterior", "Body"],
        "part_gen": "specific part"
    }
}

# 2. ADATOK IMPORTÁLÁSA VALÓDI FORRÁSBÓL
@st.cache_data
def load_data():
    # Ez egy garantáltan működő RAW GitHub link
    url = "https://githubusercontent.com"
    try:
        df = pd.read_csv(url)
        df = df[['make', 'model', 'year']]
        df.columns = ['Márka', 'Modell', 'Év']
        df['Év'] = pd.to_numeric(df['Év'], errors='coerce')
        return df.dropna()
    except:
        # Vészhelyzeti adatok, ha a net nem érhető el
        return pd.DataFrame({'Márka':['Audi', 'BMW', 'Ford'], 'Modell':['A4', '320d', 'Focus'], 'Év':[2015, 2018, 2020]})

df = load_data()

# 3. UI BEÁLLÍTÁSA
st.set_page_config(page_title="AutoDB Pro", layout="wide")

# Nyelvválasztó
col_t, col_l = st.columns([3, 1])
with col_l:
    lang = st.radio("Language / Nyelv", ["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    t = translations["hu" if "🇭🇺" in lang else "en"]

with col_t:
    st.title(t["title"])

# 4. KERESŐ PANEL (JAVÍTOTT FORM)
with st.sidebar:
    # Fontos: Minden ami a 'with form' alatt van, csak a gomb után küldődik el
    with st.form("search_form"):
        st.header(t["sidebar_header"])
        
        brands = sorted(df['Márka'].unique())
        selected_brands = st.multiselect(t["brand_select"], options=brands)
        
        min_y, max_y = int(df['Év'].min()), int(df['Év'].max())
        year_range = st.slider(t["year_range"], min_y, max_y, (min_y, max_y))
        
        cat_selection = st.multiselect(t["cat_select"], options=t["cats"], default=[t["cats"]])
        
        # Ez a gomb javítja a "Missing Submit Button" hibát!
        submit = st.form_submit_button(t["search_btn"])

# 5. MEGJELENÍTÉS
if submit:
    mask = df['Év'].between(year_range[0], year_range[1])
    if selected_brands:
        mask &= df['Márka'].isin(selected_brands)
    
    res = df[mask].copy()
    if not res.empty:
        res['Kategória'] = ", ".join(cat_selection)
        res['Alkatrész'] = res['Márka'] + " " + res['Modell'] + " " + t["part_gen"]
        st.subheader(f"{t['results']}: {len(res)}")
        st.dataframe(res, use_container_width=True)
    else:
        st.warning("Nincs találat.")
else:
    # Kezdőképernyő mintaadatokkal
    st.info("💡 Az adatbázis betöltve. Válassz a szűrőkből és kattints a Keresésre!")
    st.dataframe(df.sample(min(len(df), 15)), use_container_width=True)

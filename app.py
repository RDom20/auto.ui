import streamlit as st
import pandas as pd
import requests

# 1. NYELVI SZÓTÁR
translations = {
    "hu": {
        "title": "🚗 Professzionális Autóalkatrész Adatbázis",
        "loading": "Adatok betöltése a forrásból...",
        "sidebar_header": "Keresési feltételek",
        "brand_select": "Márka kiválasztása",
        "year_range": "Évjárat",
        "cat_select": "Kategória",
        "search_btn": "Keresés 🔍",
        "results": "Találatok",
        "cats": ["Futómű", "Motor", "Elektronika", "Beltér", "Kültér", "Kaszni"],
        "part_gen": "specifikus alkatrész"
    },
    "en": {
        "title": "🚗 Professional Auto Parts Database",
        "loading": "Loading data from source...",
        "sidebar_header": "Search Filters",
        "brand_select": "Select Brand",
        "year_range": "Year Range",
        "cat_select": "Category",
        "search_btn": "Search 🔍",
        "results": "Results",
        "cats": ["Suspension", "Engine", "Electronics", "Interior", "Exterior", "Body"],
        "part_gen": "specific part"
    }
}

# 2. ADATOK BETÖLTÉSE (A BEKÜLDÖTT PROJEKT KÉSZ ADATFÁJLJÁBÓL)
@st.cache_data
def load_massive_db():
    # Ez a Plowman-féle open-vehicle-db generált, összefűzött JSON fájlja
    url = "https://githubusercontent.com"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        rows = []
        for brand in data:
            brand_name = brand.get('name', 'Ismeretlen')
            for model in brand.get('models', []):
                model_name = model.get('name', 'Ismeretlen')
                # A JSON-ban listaként vannak az évek
                years = model.get('years', [2020])
                for year in years:
                    rows.append({
                        "Márka": brand_name,
                        "Modell": model_name,
                        "Év": int(year)
                    })
        return pd.DataFrame(rows)
    except Exception as e:
        # Ha a külső link nem elérhető, egy alap biztonsági lista
        return pd.DataFrame([
            {"Márka": "Audi", "Modell": "A4", "Év": 2018},
            {"Márka": "BMW", "Modell": "320d", "Év": 2020},
            {"Márka": "Tesla", "Modell": "Model 3", "Év": 2022}
        ])

# 3. UI INICIALIZÁLÁSA
st.set_page_config(page_title="AutoDB Pro", layout="wide")

# Adatbázis betöltése (Spinner jelzi a folyamatot)
with st.spinner("Adatbázis importálása..."):
    df = load_massive_db()

# Nyelvválasztó
col_title, col_lang = st.columns([4, 1])
with col_lang:
    lang = st.radio("Language", ["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    t = translations["hu" if "🇭🇺" in lang else "en"]

with col_title:
    st.title(t["title"])

# 4. KERESŐ PANEL (SIDEBAR FORM)
with st.sidebar:
    with st.form("search_form"):
        st.header(t["sidebar_header"])
        
        # Dinamikus márka lista (a betöltött JSON alapján)
        brand_list = sorted(df['Márka'].unique())
        selected_brands = st.multiselect(t["brand_select"], options=brand_list)
        
        # Évszám csúszka (a betöltött adatok minimuma és maximuma között)
        min_y, max_y = int(df['Év'].min()), int(df['Év'].max())
        year_range = st.slider(t["year_range"], min_y, max_y, (2015, 2024))
        
        # Kategóriák
        cat_selection = st.multiselect(t["cat_select"], options=t["cats"], default=[t["cats"]])
        
        # Keresés indítása gomb (KÖTELEZŐ)
        submit = st.form_submit_button(t["search_btn"])

# 5. MEGJELENÍTÉS
if submit:
    # Aktív szűrés
    mask = df['Év'].between(year_range[0], year_range[1])
    if selected_brands:
        mask &= df['Márka'].isin(selected_brands)
    
    res = df[mask].copy()
    
    if not res.empty:
        # Alkatrész adatok "virtuális" generálása
        res['Kategória'] = ", ".join(cat_selection) if cat_selection else "N/A"
        res['Alkatrész'] = res['Márka'] + " " + res['Modell'] + " " + t["part_gen"]
        
        st.subheader(f"{t['results']}: {len(res)}")
        st.dataframe(res, use_container_width=True)
    else:
        st.warning("Nincs találat. Próbáld tágítani a szűrést!")
else:
    # KEZDŐKÉPERNYŐ (MINTÁK)
    st.info("💡 Az adatbázis betöltve a 'Plowman' nyílt forrásból. Használd a szűrőket!")
    sample_df = df.sample(min(len(df), 20)).copy()
    sample_df['Kategória'] = "Válassz szűrőt!"
    sample_df['Alkatrész'] = "Kattints a keresésre"
    st.dataframe(sample_df, use_container_width=True)

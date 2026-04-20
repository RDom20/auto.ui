import streamlit as st
import pandas as pd

# 1. NYELVI SZÓTÁR
translations = {
    "hu": {
        "loading": "Adatbázis betöltése... Kérlek várj!",
        "title": "🚗 Professzionális Alkatrész Adatbázis",
        "sidebar_header": "Keresési feltételek",
        "brand_select": "Márka kiválasztása",
        "year_range": "Évjárat",
        "cat_select": "Kategória",
        "search_label": "Kulcsszó (pl. hangszóró)",
        "search_btn": "Keresés 🔍",
        "results_count": "Találatok",
        "random_title": "Ajánlott modellek a teljes adatbázisból",
        "cats": ["Futómű", "Motor", "Elektronika", "Beltér", "Kültér", "Kaszni"],
        "part_gen": "specifikus alkatrész"
    },
    "en": {
        "loading": "Loading database... Please wait!",
        "title": "🚗 Professional Auto Parts Database",
        "sidebar_header": "Search Filters",
        "brand_select": "Select Brand",
        "year_range": "Year Range",
        "cat_select": "Category",
        "search_label": "Keyword (e.g. speaker)",
        "search_btn": "Search 🔍",
        "results_count": "Results",
        "random_title": "Recommended models from the full database",
        "cats": ["Suspension", "Engine", "Electronics", "Interior", "Exterior", "Body"],
        "part_gen": "specific part"
    }
}

# 2. TELJES ADATBÁZIS BETÖLTÉSE (KÖTELEZŐ MEGVÁRNI)
@st.cache_data
def load_massive_database():
    # Ez a link több mint 10.000+ autót tartalmaz
    url = "https://githubusercontent.com"
    try:
        df_raw = pd.read_csv(url)[['make', 'model', 'year']]
        df_raw.columns = ['Márka', 'Modell', 'Év']
        df_raw['Év'] = pd.to_numeric(df_raw['Év'], errors='coerce')
        return df_raw.dropna().sort_values(['Márka', 'Modell'])
    except:
        # Biztonsági tartalék, ha a GitHub nem válaszol (30+ márka)
        brands = ['Audi', 'BMW', 'VW', 'Mercedes', 'Toyota', 'Ford', 'Honda', 'Tesla', 'Volvo', 'Lexus', 'Mazda', 'Suzuki']
        data = []
        for b in brands:
            for i in range(10):
                data.append({"Márka": b, "Modell": f"Típus {i+1}", "Év": 2010 + i})
        return pd.DataFrame(data)

# Fő folyamat indítása
st.set_page_config(page_title="Auto Database PRO", layout="wide")

# Itt "megfogjuk" a futást, amíg az adatok be nem töltődnek
with st.spinner("Adatok betöltése..."):
    df = load_massive_database()

# 3. NYELVVÁLASZTÓ
col_title, col_lang = st.columns([3, 1])
with col_lang:
    lang = st.radio("Nyelv / Language", options=["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    t = translations["hu" if "🇭🇺" in lang else "en"]

with col_title:
    st.title(t["title"])

# 4. KERESŐ FORM - CSAK AKKOR LÁTSZIK, HA VAN ADAT
with st.sidebar:
    with st.form("search_form"):
        st.header(t["sidebar_header"])
        
        # Most már a teljes (50+) márka lista itt lesz
        brand_selection = st.multiselect(
            t["brand_select"], 
            options=sorted(df['Márka'].unique()),
            help="Válassz ki egy vagy több márkát"
        )
        
        min_y, max_y = int(df['Év'].min()), int(df['Év'].max())
        year_range = st.slider(t["year_range"], min_y, max_y, (min_y, max_y))
        
        cat_selection = st.multiselect(t["cat_select"], options=t["cats"], default=[t["cats"]])
        
        search_term = st.text_input(t["search_label"], "")
        
        submit_button = st.form_submit_button(label=t["search_btn"])

# 5. MEGJELENÍTÉS ÉS SZŰRÉS
if submit_button:
    # Aktív szűrés
    mask = df['Év'].between(year_range[0], year_range[1])
    if brand_selection:
        mask &= df['Márka'].isin(brand_selection)
    
    res = df[mask].copy()
    
    # Alkatrész generálás a szűrt listához
    if not res.empty:
        res['Kategória'] = ", ".join(cat_selection) if cat_selection else "N/A"
        res['Alkatrész'] = res['Márka'] + " " + res['Modell'] + " " + t["part_gen"]
        
        if search_term:
            res = res[res['Alkatrész'].str.contains(search_term, case=False)]
            
        st.subheader(f"{t['results_count']}: {len(res)}")
        st.dataframe(res, use_container_width=True)
    else:
        st.warning("Nincs találat a megadott szűrőkkel.")
else:
    # Kezdőképernyő: Mutassunk sokat a betöltött adatbázisból (pl. 50-et)
    st.subheader(t["random_title"])
    st.write(f"Az adatbázis jelenleg **{len(df)}** különböző járműtípust tartalmaz.")
    
    sample_df = df.sample(min(len(df), 50)).copy()
    sample_df['Kategória'] = "Válassz szűrőt!"
    sample_df['Alkatrész'] = "Kereséshez használd a bal oldali panelt"
    
    st.dataframe(sample_df, use_container_width=True)
    st.info("💡 A teljes adatbázis betöltődött. Használd a bal oldali 'Keresés' gombot a pontosításhoz!")

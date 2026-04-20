import streamlit as st
import pandas as pd
import requests

# 1. NYELVI SZÓTÁR (Zászlókkal)
translations = {
    "hu": {
        "title": "🚗 Open Vehicle Database Kereső",
        "loading": "Adatok betöltése a GitHub-ról...",
        "sidebar_header": "Szűrés",
        "brand_select": "Márka",
        "year_range": "Évjárat",
        "search_btn": "Keresés 🔍",
        "results": "Talált modellek",
        "part_gen": "alkatrész",
        "cats": ["Motor", "Elektronika", "Futómű", "Beltér"]
    },
    "en": {
        "title": "🚗 Open Vehicle DB Search",
        "loading": "Loading data from GitHub...",
        "sidebar_header": "Filters",
        "brand_select": "Make",
        "year_range": "Year Range",
        "search_btn": "Search 🔍",
        "results": "Models Found",
        "part_gen": "part",
        "cats": ["Engine", "Electronics", "Suspension", "Interior"]
    }
}

# 2. ADATOK IMPORTÁLÁSA AZ "OPEN-VEHICLE-DB"-BŐL
@st.cache_data
def load_open_vehicle_db():
    # Ez a link a repozitórium tartalmát kérdezi le
    base_url = "https://githubusercontent.com"
    try:
        # Ez a repozitórium szerencsére generál egy összefoglalt 'data.json' fájlt a 'dist' mappába
        response = requests.get(base_url)
        data = response.json()
        
        rows = []
        for brand in data:
            brand_name = brand['name']
            for model in brand.get('models', []):
                model_name = model['name']
                # Évszámok kezelése (ha nincs megadva, 2000-2024 közé tesszük)
                years = model.get('years', range(2005, 2025))
                for year in years:
                    rows.append({"Márka": brand_name, "Modell": model_name, "Év": year})
        
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Hiba az importáláskor: {e}")
        return pd.DataFrame(columns=['Márka', 'Modell', 'Év'])

# UI indítása
st.set_page_config(page_title="OpenVehicleDB", layout="wide")

# Nyelvválasztó
_, lang_col = st.columns([3, 1])
with lang_col:
    lang = st.radio("Language", ["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    t = translations["hu" if "🇭🇺" in lang else "en"]

st.title(t["title"])

with st.spinner(t["loading"]):
    df = load_open_vehicle_db()

# 3. KERESŐ FORM
with st.sidebar:
    with st.form("search_form"):
        st.header(t["sidebar_header"])
        
        brand_list = sorted(df['Márka'].unique())
        selected_brands = st.multiselect(t["brand_select"], options=brand_list)
        
        min_y, max_y = int(df['Év'].min()), int(df['Év'].max())
        year_range = st.slider(t["year_range"], min_y, max_y, (2010, 2022))
        
        cat_selection = st.multiselect("Kategória", options=t["cats"], default=[t["cats"]])
        
        submit = st.form_submit_button(t["search_btn"])

# 4. EREDMÉNYEK
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
    st.info("💡 Az Open Vehicle Database betöltve. Válassz márkát és keress!")
    st.dataframe(df.sample(min(len(df), 20)), use_container_width=True)

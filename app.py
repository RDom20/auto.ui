import streamlit as st
import pandas as pd
import requests

# 1. NYELVI SZÓTÁR
translations = {
    "hu": {
        "title": "🚗 Élő Globális Autóalkatrész Adatbázis",
        "loading": "Adatok lekérése a hivatalos szerverekről...",
        "sidebar_header": "Keresési feltételek",
        "brand_select": "Márka kiválasztása",
        "year_range": "Évjárat",
        "cat_select": "Kategória",
        "search_btn": "Keresés indítása 🔍",
        "results": "Talált modellek",
        "cats": ["Futómű", "Motor", "Elektronika", "Beltér", "Kültér", "Kaszni"],
        "part_gen": "specifikus alkatrész"
    },
    "en": {
        "title": "🚗 Live Global Auto Parts Database",
        "loading": "Fetching data from official servers...",
        "sidebar_header": "Search Filters",
        "brand_select": "Select Brand",
        "year_range": "Year Range",
        "cat_select": "Category",
        "search_btn": "Start Search 🔍",
        "results": "Models Found",
        "cats": ["Suspension", "Engine", "Electronics", "Interior", "Exterior", "Body"],
        "part_gen": "specific part"
    }
}

# 2. ÉLŐ ADATLEKÉRÉS AZ NHTSA API-BÓL
@st.cache_data
def get_all_brands():
    # Lekérjük az összes hivatalos autógyártót
    url = "https://dot.gov"
    response = requests.get(url).json()
    brands = [item['Make_Name'] for item in response['Results']]
    return sorted(brands)

def get_models_for_make(make):
    # Lekérjük egy adott márka összes modelljét
    url = f"https://dot.gov{make}?format=json"
    response = requests.get(url).json()
    models = [item['Model_Name'] for item in response['Results']]
    return sorted(list(set(models)))

# 3. UI BEÁLLÍTÁSA
st.set_page_config(page_title="Live Auto DB", layout="wide")

# Nyelvválasztó
_, lang_col = st.columns([4, 1])
with lang_col:
    lang = st.radio("Nyelv", ["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    t = translations["hu" if "🇭🇺" in lang else "en"]

st.title(t["title"])

# Adatok betöltése
with st.spinner(t["loading"]):
    all_brands = get_all_brands()

# 4. KERESŐ PANEL
with st.sidebar:
    with st.form("search_form"):
        st.header(t["sidebar_header"])
        
        # Itt már több ezer márka van!
        selected_make = st.selectbox(t["brand_select"], options=all_brands, index=all_brands.index("BMW") if "BMW" in all_brands else 0)
        
        year = st.slider(t["year_range"], 1995, 2025, (2015, 2023))
        
        cat_selection = st.multiselect(t["cat_select"], options=t["cats"], default=[t["cats"]])
        
        submit = st.form_submit_button(t["search_btn"])

# 5. EREDMÉNYEK MEGJELENÍTÉSE
if submit:
    with st.spinner(f"Modellek betöltése: {selected_make}..."):
        models = get_models_for_make(selected_make)
        
        if models:
            # Táblázat összeállítása
            data = []
            for m in models:
                data.append({
                    "Márka": selected_make,
                    "Modell": m,
                    "Év": f"{year}-{year}",
                    "Kategória": ", ".join(cat_selection),
                    "Alkatrész": f"{selected_make} {m} {t['part_gen']}"
                })
            
            df_res = pd.DataFrame(data)
            st.subheader(f"{t['results']}: {selected_make}")
            st.dataframe(df_res, use_container_width=True)
        else:
            st.warning("Nem találtunk modellt ehhez a márkához.")
else:
    st.info("💡 Válassz egy márkát a listából (több ezer van!) és nyomj a keresésre.")

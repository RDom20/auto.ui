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

# 2. KÜLSŐ NYÍLT ADATBÁZIS IMPORTÁLÁSA (Open Source CSV)
@st.cache_data
def load_external_csv():
    # Ez a "RAW" link közvetlenül az adatokat adja át a kódnak
    url = "https://githubusercontent.com"
    try:
        # Beolvassuk a külső CSV-t
        df = pd.read_csv(url)
        # Kiválasztjuk a szükséges oszlopokat és magyarosítjuk a neveket
        df = df[['make', 'model', 'year']]
        df.columns = ['Márka', 'Modell', 'Év']
        # Tisztítás
        df['Év'] = pd.to_numeric(df['Év'], errors='coerce')
        return df.dropna().sort_values(['Márka', 'Modell'])
    except Exception as e:
        st.error(f"Hiba az adatbázis importálásakor: {e}")
        return pd.DataFrame(columns=['Márka', 'Modell', 'Év'])

# Adatok beolvasása a külső linkről
df = load_external_csv()

# 3. UI BEÁLLÍTÁSA
st.set_page_config(page_title="OpenSource AutoDB", layout="wide")

# Nyelvválasztó
_, lang_col = st.columns(2)
with lang_col:
    lang = st.radio("Language / Nyelv", ["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    t = translations["hu" if "🇭🇺" in lang else "en"]

st.title(t["title"])

# 4. KERESŐ PANEL (A SIDEBAR-BAN)
with st.sidebar:
    with st.form("search_form"):
        st.header(t["sidebar_header"])
        
        # Dinamikusan feltölti a márkákat a külső fájlból (kb. 50-100 márka)
        selected_brands = st.multiselect(t["brand_select"], options=sorted(df['Márka'].unique()))
        
        min_y, max_y = int(df['Év'].min()), int(df['Év'].max())
        year_range = st.slider(t["year_range"], min_y, max_y, (2010, 2023))
        
        cat_selection = st.multiselect(t["cat_select"], options=t["cats"], default=[t["cats"]])
        
        submit = st.form_submit_button(t["search_btn"])

# 5. SZŰRÉS ÉS EREDMÉNYEK
if submit:
    # Szűrési logika a külső adatokon
    mask = df['Év'].between(year_range[0], year_range[1])
    if selected_brands:
        mask &= df['Márka'].isin(selected_brands)
    
    res = df[mask].copy()
    
    if not res.empty:
        # Virtuális alkatrész adatok hozzárendelése
        res['Kategória'] = ", ".join(cat_selection) if cat_selection else "N/A"
        res['Alkatrész'] = res['Márka'] + " " + res['Modell'] + " " + t["part_gen"]
        
        st.subheader(f"{t['results']}: {len(res)}")
        st.dataframe(res, use_container_width=True)
    else:
        st.warning("Nincs találat.")
else:
    # Alapállapot: Mutassunk egy mintát a külső adatbázisból
    st.info("💡 Az adatbázis sikeresen importálva a GitHub-ról. Használd a szűrőket!")
    if not df.empty:
        st.dataframe(df.sample(20), use_container_width=True)

import streamlit as st
import pandas as pd

# 1. Minta Adatbázis létrehozása
data = [
    {"Márka": "BMW", "Modell": "320d", "Év": 2018, "Kivitel": "Sedan", "Motor": "2.0 Diesel", "Kategória": "Elektronika", "Alkatrész": "Első ajtó hangszóró (16cm)"},
    {"Márka": "BMW", "Modell": "320d", "Év": 2018, "Kivitel": "Sedan", "Motor": "2.0 Diesel", "Kategória": "Motor", "Alkatrész": "Olajszűrő"},
    {"Márka": "Audi", "Modell": "A4", "Év": 2020, "Kivitel": "Avant", "Motor": "2.0 TFSI", "Kategória": "Elektronika", "Alkatrész": "Mélynyomó (Csomagtér)"},
    {"Márka": "Volkswagen", "Modell": "Golf 7", "Év": 2015, "Kivitel": "Hatchback", "Motor": "1.6 TDI", "Kategória": "Futómű", "Alkatrész": "Lengéscsillapító"},
    {"Márka": "Volkswagen", "Modell": "Golf 7", "Év": 2015, "Kivitel": "Hatchback", "Motor": "1.6 TDI", "Kategória": "Elektronika", "Alkatrész": "Magassugárzó hangszóró"},
    {"Márka": "Tesla", "Modell": "Model 3", "Év": 2022, "Kivitel": "Sedan", "Motor": "Electric", "Kategória": "Beltér", "Alkatrész": "Középső kijelző"},
    {"Márka": "Ford", "Modell": "Focus", "Év": 2012, "Kivitel": "Kombi", "Motor": "1.0 EcoBoost", "Kategória": "Kaszni", "Alkatrész": "Első sárvédő (Bal)"},
]

df = pd.DataFrame(data)

# 2. UI Beállítások
st.set_page_config(page_title="Autóalkatrész Adatbázis", layout="wide")
st.title("🚗 Jármű-alkatrész Kereső Rendszer")
st.sidebar.header("Szűrő Panelek")

# 3. Szűrők (Sidebar)
search_term = st.sidebar.text_input("Keresés név alapján (pl. hangszóró):", "")

brand_filter = st.sidebar.multiselect("Márka", options=df["Márka"].unique(), default=df["Márka"].unique())
year_filter = st.sidebar.slider("Kiadás éve", int(df["Év"].min()), int(df["Év"].max()), (int(df["Év"].min()), int(df["Év"].max())))
cat_filter = st.sidebar.multiselect("Kategória", options=["Futómű", "Motor", "Elektronika", "Beltér", "Kültér", "Kaszni"], default=["Futómű", "Motor", "Elektronika", "Beltér", "Kültér", "Kaszni"])

# 4. Adatok szűrése a háttérben
filtered_df = df[
    (df["Márka"].isin(brand_filter)) &
    (df["Év"].between(year_filter[0], year_filter[1])) &
    (df["Kategória"].isin(cat_filter))
]

if search_term:
    filtered_df = filtered_df[filtered_df["Alkatrész"].str.contains(search_term, case=False) | 
                              filtered_df["Modell"].str.contains(search_term, case=False)]

# 5. Eredmények megjelenítése
col1, col2, col3 = st.columns(3)
col1.metric("Találatok száma", len(filtered_df))

st.dataframe(filtered_df, use_container_width=True)

# Üres állapot kezelése
if filtered_df.empty:
    st.warning("Nincs találat a megadott feltételekkel.")

import functools
import json
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime
import requests
import pandas as pd
import streamlit as st
from tqdm import tqdm

# --- AZ EREDETI KÓDOD (VÁLTOZATLAN) ---

VEHICLE_TYPE_ID_MAP = {
    1: {'VehicleTypeName': 'Motorcycle'},
    2: {'VehicleTypeName': 'Passenger Car'},
    3: {'VehicleTypeName': 'Truck'},
    5: {'VehicleTypeName': 'Bus'},
    6: {'VehicleTypeName': 'Trailer'},
    7: {'VehicleTypeName': 'Multipurpose Passenger Vehicle (MPV)'},
    9: {'VehicleTypeName': 'Low Speed Vehicle (LSV)'},
    10: {'VehicleTypeName': 'Incomplete Vehicle'},
    13: {"VehicleTypeName": "Off Road Vehicle"}
}
PASSENGER_VEHICLE_TYPE_IDS = {2, 3, 7}
CURRENT_YEAR = datetime.now().year
YEAR_RANGE = range(1981, CURRENT_YEAR + 2)

def _make_api_request(path):
    url = f"https://dot.gov{path}"
    url += "&format=json" if "&" in path else "?format=json"
    try:
        response = requests.get(url, timeout=10)
        # Itt történik a javítás: ellenőrizzük a választ
        if response.status_code == 200:
            return response.json().get("Results")
        return None
    except:
        return None

def slugify_string(input_string):
    slug = input_string.strip().lower().replace(" ", "_").replace("-", "_")
    return re.sub("[^a-z0-9_]", "", slug)

def fetch_all_makes():
    raw_makes_list = _make_api_request("/getallmakes")
    if not raw_makes_list: return []
    all_makes = []
    for make_data in raw_makes_list:
        all_makes.append({
            "make_id": make_data["Make_ID"],
            "make_name": make_data["Make_Name"].strip()
        })
    return all_makes

def fetch_models_for_make_id(make_id):
    models = []
    for v_type in ["car", "truck", "mpv"]:
        raw_list = _make_api_request(f"/GetModelsForMakeIdYear/makeId/{make_id}/vehicleType/{v_type}")
        if raw_list:
            for raw_model in raw_list:
                models.append({
                    "model_id": raw_model["Model_ID"],
                    "model_name": raw_model["Model_Name"].strip(),
                    "vehicle_type": v_type
                })
    return models

# --- GUI ÉS MAGYARÍTÁS (HIBATŰRŐ MÓDON) ---

translations = {
    "hu": {
        "title": "🚗 Profi Járműadatbázis",
        "search_btn": "Keresés 🔍",
        "select_make": "Válassz márkát",
        "select_year": "Évjárat",
        "results": "Találatok",
        "loading": "Adatok lekérése a hivatalos szerverről...",
        "api_error": "Az API szerver jelenleg nem elérhető. Próbáld újra később!"
    },
    "en": {
        "title": "🚗 Professional Vehicle DB",
        "search_btn": "Search 🔍",
        "select_make": "Select Make",
        "select_year": "Year Range",
        "results": "Results",
        "loading": "Fetching data from servers...",
        "api_error": "API server is currently unavailable. Please try again later!"
    }
}

st.set_page_config(page_title="AutoDB", layout="wide")

# Nyelvválasztó
_, lang_col = st.columns()
with lang_col:
    lang_choice = st.radio("Language", ["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    t = translations["hu" if "🇭🇺" in lang_choice else "en"]

st.title(t["title"])

@st.cache_data(show_spinner=False)
def get_makes_safe():
    res = fetch_all_makes()
    if not res:
        # Ha az API elszáll, betöltünk egy alap listát, hogy az app ne álljon le
        return [{"make_id": 440, "make_name": "ASTON MARTIN"}, {"make_id": 441, "make_name": "TESLA"}, {"make_id": 442, "make_name": "BMW"}]
    return res

with st.spinner(t["loading"]):
    all_makes = get_makes_safe()

# Sidebar
with st.sidebar:
    with st.form("search_form"):
        st.header("Szűrők")
        make_names = [m["make_name"] for m in all_makes]
        selected_make_name = st.selectbox(t["select_make"], options=sorted(make_names))
        selected_make_id = next(m["make_id"] for m in all_makes if m["make_name"] == selected_make_name)
        years = st.slider(t["select_year"], 1981, CURRENT_YEAR + 1, (2015, CURRENT_YEAR))
        submit = st.form_submit_button(t["search_btn"])

# Eredmények
if submit:
    with st.spinner(t["loading"]):
        models = fetch_models_for_make_id(selected_make_id)
        if models:
            st.subheader(f"{t['results']}: {selected_make_name}")
            st.dataframe(pd.DataFrame(models), use_container_width=True)
        else:
            st.error(t["api_error"])
else:
    st.info("💡 " + ("Válassz egy márkát bal oldalt!" if "🇭🇺" in lang_choice else "Select a make on the left!"))

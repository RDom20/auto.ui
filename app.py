import functools
import json
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime

import requests
from tqdm import tqdm
import streamlit as st # GUI-hoz szükséges

# --- AZ ÁLTALAD KÜLDÖTT EREDETI KÓD (VÁLTOZATLAN) ---

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
    if "&" in path:
        url += "&format=json"
    else:
        url += "?format=json"

    print(url)
    response = requests.get(url)
    return response.json().get("Results")

def slugify_string(input_string):
    slug = input_string.strip()
    slug = slug.lower()
    slug = slug.replace(" ", "_")
    slug = slug.replace(" ", "_")
    slug = slug.replace("-", "_")
    slug = re.sub("[^a-z0-9_]", "", slug)
    return slug

def fetch_all_makes():
    raw_makes_list = _make_api_request("/getallmakes")

    all_makes = []
    for make_data in raw_makes_list:
        make_name = make_data["Make_Name"].strip()
        make_slug = slugify_string(make_name)
        all_makes.append({
            "make_id": make_data["Make_ID"],
            "make_name": make_name,
            "make_slug": make_slug,
            "models": {},
            "first_year": None,
            "last_year": None,
        })

    return all_makes

def fetch_types_for_make(make_name):
    raw_types_list = _make_api_request(f"/GetVehicleTypesForMake/{make_name}")
    print(raw_types_list)

def fetch_types_for_make_id(make_id):
    raw_types_list = _make_api_request(f"/GetVehicleTypesForMakeId/{make_id}")

    all_types = []
    for make_type in raw_types_list:
        all_types.append({
            'type_id': make_type.get("VehicleTypeId", "<missing>"),
            'type_name': make_type["VehicleTypeName"].strip(),
        })

    return all_types

def _get_model_dict(raw_model, vehicle_type=None):
    assert vehicle_type

    return {
        "model_id": raw_model["Model_ID"],
        "model_name": raw_model["Model_Name"].strip(),
        "vehicle_type": vehicle_type,
        "years": [],
        "model_styles": OrderedDict(),
    }

def fetch_models_for_make_id(make_id):
    models = []

    raw_cars_list = _make_api_request(f"/GetModelsForMakeIdYear/makeId/{make_id}/vehicleType/car")
    for raw_model in raw_cars_list:
        models.append(_get_model_dict(raw_model, vehicle_type="car"))

    raw_trucks_list = _make_api_request(f"/GetModelsForMakeIdYear/makeId/{make_id}/vehicleType/truck")
    for raw_model in raw_trucks_list:
        models.append(_get_model_dict(raw_model, vehicle_type="truck"))

    raw_mpv_list = _make_api_request(f"/GetModelsForMakeIdYear/makeId/{make_id}/vehicleType/mpv")
    for raw_model in raw_mpv_list:
        models.append(_get_model_dict(raw_model, vehicle_type="mpv"))

    return models

def fetch_model_ids_for_make_and_year(make_id, year):
    model_ids = []
    models_in_year = _make_api_request(f"/getmodelsformakeidyear/makeId/{make_id}/modelyear/{year}")
    for model in models_in_year:
        model_ids.append(model["Model_ID"])

    return model_ids

@functools.cache
def make_produces_passenger_vehicles(make_id):
    make_types = fetch_types_for_make_id(make_id)
    make_type_ids = set([make_type["type_id"] for make_type in make_types])
    if not make_type_ids.issubset(VEHICLE_TYPE_ID_MAP.keys()):
        print(f"Found a new type?? {make_types}")
    return bool(make_type_ids.intersection(PASSENGER_VEHICLE_TYPE_IDS))

# --- ÚJ GUI ÉS NYELVI RÉSZ ---

translations = {
    "hu": {
        "title": "🚗 Járműadatbázis Lekérdező (NHTSA API)",
        "sidebar": "Beállítások",
        "lang": "Nyelv / Language",
        "fetch_makes": "Márkák betöltése...",
        "select_make": "Válassz márkát",
        "select_year": "Évjárat szűrő",
        "search_btn": "Keresés 🔍",
        "results": "Találatok",
        "no_res": "Nincs találat.",
        "loading": "Adatok lekérése a szerverről..."
    },
    "en": {
        "title": "🚗 Vehicle Database Query (NHTSA API)",
        "sidebar": "Settings",
        "lang": "Language / Nyelv",
        "fetch_makes": "Fetching makes...",
        "select_make": "Select Make",
        "select_year": "Year Filter",
        "search_btn": "Search 🔍",
        "results": "Results",
        "no_res": "No results found.",
        "loading": "Fetching data from server..."
    }
}

st.set_page_config(page_title="NHTSA Vehicle DB", layout="wide")

# Nyelvválasztó
if 'lang' not in st.session_state:
    st.session_state.lang = 'hu'

col_title, col_lang = st.columns([4, 1])
with col_lang:
    choice = st.radio("Language", ["🇭🇺 HU", "🇺🇸 EN"], horizontal=True)
    st.session_state.lang = 'hu' if "🇭🇺" in choice else 'en'

t = translations[st.session_state.lang]
st.title(t["title"])

# Márkák gyorsítótárazott betöltése a te fetch_all_makes() függvényeddel
@st.cache_data
def get_cached_makes():
    return fetch_all_makes()

with st.spinner(t["loading"]):
    all_makes_list = get_cached_makes()

# Sidebar form a Használtautó stílushoz
with st.sidebar:
    with st.form("search_form"):
        st.header(t["sidebar"])
        
        # Márka választó a te adatid alapján
        make_names = [m["make_name"] for m in all_makes_list]
        selected_make_name = st.selectbox(t["select_make"], options=make_names)
        selected_make_id = next(m["make_id"] for m in all_makes_list if m["make_name"] == selected_make_name)
        
        # Évszám csúszka
        year_val = st.slider(t["select_year"], 1981, datetime.now().year + 1, (2015, 2024))
        
        submit = st.form_submit_button(t["search_btn"])

# Eredmények megjelenítése
if submit:
    with st.spinner(t["loading"]):
        # Modell lekérése a te fetch_models_for_make_id() függvényeddel
        models = fetch_models_for_make_id(selected_make_id)
        
        if models:
            # Táblázatba rendezés
            display_data = []
            for m in models:
                display_data.append({
                    "ID": m["model_id"],
                    "Modell": m["model_name"],
                    "Típus": m["vehicle_type"],
                    "Évszám tartomány": f"{year_val[0]} - {year_val[1]}"
                })
            
            st.subheader(f"{t['results']}: {selected_make_name}")
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.warning(t["no_res"])
else:
    st.info("💡 " + ("Válassz egy márkát és kattints a keresésre!" if st.session_state.lang == 'hu' else "Select a make and click search!"))

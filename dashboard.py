
# -----------------------------
# 10. (Optional) Streamlit dashboard in separate file
# -----------------------------
# See dashboard.py (not executed here). Create it if needed.


# -----------------------------
# dashboard.py (Streamlit UI)
# -----------------------------
# Save this as dashboard.py next to main.py. Run with:
#   streamlit run dashboard.py
# It reloads on save and lets you tweak costs, speeds, toll delays, etc.

import json
import math
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Delhi–Vizag Corridor Dashboard", layout="wide")

# ---------- Utility funcs ----------

def fmt_hhmm(minutes):
    if pd.isna(minutes):
        return ""
    h = int(minutes // 60)
    m = int(round(minutes % 60))
    return f"{h:02d}:{m:02d}"

@st.cache_data
def load_geojson(path):
    with open(path) as f:
        return json.load(f)

@st.cache_data
def load_segments(csv_path):
    df = pd.read_csv(csv_path)
    return df

@st.cache_data
def explode_lines(gj):
    rows = []
    for ft in gj.get("features", []):
        if ft.get("geometry", {}).get("type") != "LineString":
            continue
        props = ft.get("properties", {})
        seg_id = props.get("segment_id")
        seg_name = props.get("segment_name") or props.get("name") or "Unnamed Segment"
        corridor = props.get("corridor") or "Unknown Corridor"
        coords = ft["geometry"]["coordinates"]
        for order, (lon, lat) in enumerate(coords, start=1):
            rows.append({
                "segment_id": seg_id,
                "segment_name": seg_name,
                "corridor": corridor,
                "order": order,
                "lon": lon,
                "lat": lat,
            })
    return pd.DataFrame(rows)

# ---------- Sidebar inputs ----------
geojson_file = st.sidebar.text_input("Corridor GeoJSON", "corridors_clean.geojson")
seg_csv_file = st.sidebar.text_input("Segment Stats CSV", "segment_stats.csv")

baseline_km = st.sidebar.number_input("Baseline distance (km)", 0.0, 5000.0, 1240.0, 10.0)
baseline_hr = st.sidebar.number_input("Baseline time (hours)", 0.0, 72.0, 24.0, 0.5)
toll_delay = st.sidebar.number_input("Toll/Fuel delays (minutes)", 0.0, 180.0, 35.0, 5.0)

st.sidebar.markdown("### Cost assumptions")
truck_opex = st.sidebar.number_input("Truck OPEX (₹/km)", 10, 100, 35)
payload_tons = st.sidebar.number_input("Avg payload (tons)", 5, 35, 18)
yearly_trips = st.sidebar.number_input("Trips per year", 1000, 200000, 45000, 1000)

mode = st.sidebar.radio("Speed profile", ["car", "truck"], index=0)

# ---------- Load data ----------
if not Path(seg_csv_file).exists() or not Path(geojson_file).exists():
    st.error("Make sure corridors_clean.geojson and segment_stats.csv exist (run main.py first).")
    st.stop()

seg_df = load_segments(seg_csv_file)
geojson = load_geojson(geojson_file)
lines_df = explode_lines(geojson)

# total km/min from seg_df
total_km = seg_df.distance_km.sum()
# main.py stored minutes without toll delays; add them here
total_min = seg_df.est_time_min.sum() + toll_delay

# Scenario calcs
km_saved = baseline_km - total_km
min_saved = baseline_hr*60 - total_min
cost_drop_rs_trip = km_saved * truck_opex
rs_per_ton = cost_drop_rs_trip / payload_tons if payload_tons else 0
truck_days_saved = (min_saved/60/24) * yearly_trips

# ---------- Layout ----------
col1, col2 = st.columns([1,2])
with col1:
    st.markdown("## Key KPIs")
    kpis = pd.DataFrame([
        ("Expressway distance (km)", f"{total_km:,.1f}"),
        ("Expressway time (hh:mm)", fmt_hhmm(total_min)),
        ("Distance saved vs baseline (km)", f"{km_saved:,.1f}"),
        ("Time saved vs baseline", fmt_hhmm(min_saved)),
        ("₹ saved / trip", f"{cost_drop_rs_trip:,.0f}"),
        ("₹ saved / ton", f"{rs_per_ton:,.2f}"),
        ("Truck-days saved / year", f"{truck_days_saved:,.0f}"),
    ], columns=["Metric","Value"])
    st.dataframe(kpis, use_container_width=True)

    if Path("population_served.csv").exists():
        pop_df = pd.read_csv("population_served.csv")
        st.markdown("### Population Served")
        st.dataframe(pop_df, use_container_width=True)

with col2:
    st.markdown("## Segment Distance & Time")
    fig_bar = px.bar(seg_df, x="segment_name", y="distance_km", color="corridor",
                     hover_data={"est_time_hh:mm":True}, title="Segment Distances (km)")
    st.plotly_chart(fig_bar, use_container_width=True)

# Map
st.markdown("## Interactive Map")
fig_map = px.line_mapbox(
    lines_df,
    lat="lat", lon="lon",
    color="corridor",
    hover_name="segment_name",
    mapbox_style="carto-positron",
    zoom=4.5, height=700
)
# wildlife points if present
wild = [ft for ft in geojson.get("features", []) if ft.get("geometry", {}).get("type") == "Point" and ft.get("properties",{}).get("status")]
if wild:
    wild_df = pd.DataFrame([
        {
            "lat": ft["geometry"]["coordinates"][1],
            "lon": ft["geometry"]["coordinates"][0],
            **ft.get("properties", {})
        } for ft in wild
    ])
    for status, sub in wild_df.groupby("status"):
        fig_map.add_scattermapbox(lat=sub.lat, lon=sub.lon, mode="markers", name=f"Wildlife {status.title()}")

st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")
st.caption("Adjust values in the sidebar to see savings & KPIs update.")

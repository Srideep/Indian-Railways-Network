"""
Corridor map generator (Pure Python + Pandas)
- Reads one or more GeoJSONs (LineStrings + optional Points)
- Computes per-segment distances & ETAs
- Re-exports a cleaned GeoJSON
- Plots with Plotly (OpenStreetMap style)

requirements.txt
    plotly
    pandas
    flask
"""

import argparse
import json
import math
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, send_file

# -----------------------
# 0. CLI: speed profile & files
# -----------------------
parser = argparse.ArgumentParser(description="Plot corridors from GeoJSON & compute stats")
parser.add_argument(
    "--mode", choices=["car", "truck"], default="car", help="Speed profile"
)
parser.add_argument(
    "--geojson", nargs="+", default=["corridors.geojson", "dme.geojson"],
    help="One or more input GeoJSON files (space-separated)"
)
args = parser.parse_args()

SPEED_PROFILES = {
    "car": {
        # Delhi–Vizag spine
        "Delhi–Agra": 100,
        "Agra–Gwalior Expy": 95,
        "Gwl–Lakh Expy Sec‑1": 90,
        "Gwl–Lakh Expy Sec‑2": 90,
        "Lakhnadon–Raipur Expy": 95,
        "Raipur–Vizag Expy (NH-130CD)": 95,
        # Delhi–Mumbai expressway splits
        "Delhi–Vadodara": 100,
        "Vadodara–Mumbai": 95,
        "_default": 90,
    },
    "truck": {
        "Delhi–Agra": 75,
        "Agra–Gwalior Expy": 70,
        "Gwl–Lakh Expy Sec‑1": 65,
        "Gwl–Lakh Expy Sec‑2": 65,
        "Lakhnadon–Raipur Expy": 70,
        "Raipur–Vizag Expy (NH-130CD)": 70,
        "Delhi–Vadodara": 75,
        "Vadodara–Mumbai": 70,
        "_default": 65,
    },
}
SPEEDS = SPEED_PROFILES[args.mode]

# -----------------------
# 1. Load & clean GeoJSON(s)
# -----------------------
def load_and_clean_geojson(filepath: Path):
    with filepath.open("r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)  # strip JS-style comments
    return json.loads(content)

all_line_feats = []
all_point_feats = []

for fp in args.geojson:
    p = Path(fp)
    if not p.exists():
        print(f"WARNING: {fp} not found, skipping.")
        continue
    gj = load_and_clean_geojson(p)
    feats = gj.get("features", [])
    all_line_feats += [ft for ft in feats if ft.get("geometry", {}).get("type") == "LineString"]
    all_point_feats += [ft for ft in feats if ft.get("geometry", {}).get("type") == "Point"]

if not all_line_feats:
    raise ValueError("No LineString features found in provided GeoJSON files.")

print(f"Loaded {len(all_line_feats)} LineString features and {len(all_point_feats)} Point features")

# -----------------------
# 2. Explode LineStrings
# -----------------------
rows = []
for ft in all_line_feats:
    props = ft.get("properties", {})
    seg_id = props.get("segment_id") or props.get("id") or f"seg_{len(rows)}"
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
            **{k: v for k, v in props.items() if k not in {"segment_id","id","segment_name","name","corridor"}},
        })

lines_df = pd.DataFrame(rows).sort_values(["segment_id","order"]).reset_index(drop=True)
print(f"Exploded to {len(lines_df)} coordinate points")

# -----------------------
# 3. Distance & ETA
# -----------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi  = math.radians(lat2 - lat1)
    dlmb  = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlmb/2)**2
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1-a))

delta_km = [0.0]
for i in range(1, len(lines_df)):
    if lines_df.loc[i, "segment_id"] == lines_df.loc[i-1, "segment_id"]:
        d = haversine(lines_df.loc[i-1,"lat"], lines_df.loc[i-1,"lon"],
                      lines_df.loc[i,  "lat"], lines_df.loc[i,  "lon"])
    else:
        d = 0.0
    delta_km.append(d)

lines_df["delta_km"]     = delta_km
lines_df["seg_cum_km"]   = lines_df.groupby("segment_id")["delta_km"].cumsum()
lines_df["total_cum_km"] = lines_df["delta_km"].cumsum()

def eta_minutes(row):
    spd = SPEEDS.get(row["corridor"], SPEEDS["_default"])
    return (row["delta_km"] / spd) * 60 if spd else None

lines_df["delta_min"]     = lines_df.apply(eta_minutes, axis=1)
lines_df["seg_cum_min"]   = lines_df.groupby("segment_id")["delta_min"].cumsum()
lines_df["total_cum_min"] = lines_df["delta_min"].cumsum()

def fmt_hhmm(minutes):
    if pd.isna(minutes): return ""
    h = int(minutes // 60); m = int(round(minutes % 60))
    return f"{h:02d}:{m:02d}"

lines_df["delta_hhmm"]     = lines_df["delta_min"].apply(fmt_hhmm)
lines_df["seg_cum_hhmm"]   = lines_df["seg_cum_min"].apply(fmt_hhmm)
lines_df["total_cum_hhmm"] = lines_df["total_cum_min"].apply(fmt_hhmm)

# -----------------------
# 4. Segment summary CSV
# -----------------------
seg_summary = (
    lines_df.groupby(["segment_id","segment_name","corridor"], dropna=False)
            .agg(distance_km=("delta_km","sum"),
                 est_time_min=("delta_min","sum"))
            .reset_index()
)
seg_summary["est_time_hh:mm"] = seg_summary["est_time_min"].apply(fmt_hhmm)
seg_summary.to_csv("segment_stats.csv", index=False)
print("Segment statistics saved to segment_stats.csv")

# -----------------------
# 5. Rebuild combined GeoJSON
# -----------------------
line_features = []
for seg_id, seg in lines_df.groupby("segment_id", sort=False):
    coords = list(zip(seg["lon"], seg["lat"]))
    props = {
        "segment_id": seg_id,
        "segment_name": seg["segment_name"].iloc[0],
        "corridor": seg["corridor"].iloc[0],
        "distance_km": float(seg["delta_km"].sum()),
        "est_time_min": float(seg["delta_min"].sum()),
        "est_time_hhmm": fmt_hhmm(seg["delta_min"].sum()),
    }
    line_features.append({
        "type": "Feature",
        "properties": props,
        "geometry": {"type": "LineString", "coordinates": coords},
    })

geojson_out = {
    "type": "FeatureCollection",
    "features": line_features + all_point_feats,
}
with open("corridors_clean.geojson", "w") as f:
    json.dump(geojson_out, f, indent=2)
print("Enhanced GeoJSON saved to corridors_clean.geojson")

# -----------------------
# 6. Plotly map
# -----------------------
hover_cols = {
    "delta_km": ":.2f",
    "seg_cum_km": ":.2f",
    "total_cum_km": ":.2f",
    "delta_hhmm": True,
    "seg_cum_hhmm": True,
    "total_cum_hhmm": True,
}

fig = px.line_mapbox(
    lines_df,
    lat="lat",
    lon="lon",
    color="corridor",
    hover_name="segment_name",
    hover_data=hover_cols,
    mapbox_style="carto-positron",
    zoom=5,
    height=720,
    title=f"India's High-Speed Corridors (Mode: {args.mode.title()})"
)

# Point markers
if all_point_feats:
    point_lons = [ft["geometry"]["coordinates"][0] for ft in all_point_feats]
    point_lats = [ft["geometry"]["coordinates"][1] for ft in all_point_feats]
    point_names = [ft.get("properties", {}).get("name", "Point") for ft in all_point_feats]

    fig.add_trace(
        go.Scattermapbox(
            lat=point_lats,
            lon=point_lons,
            mode="markers+text",
            text=point_names,
            textposition="top center",
            marker=dict(size=11, color="red"),
            name="Points",
        )
    )

fig.update_layout(
    margin=dict(r=0, t=40, l=0, b=0),
    legend_title="Corridor",
    mapbox=dict(center=dict(lat=22.0, lon=78.0), zoom=4.7)
)
fig.write_html("corridors_map.html", include_plotlyjs="cdn", auto_open=True)
print("Interactive map saved to corridors_map.html")

# -----------------------
# 7. Console summary
# -----------------------
total_km = lines_df["delta_km"].sum()
total_min = lines_df["delta_min"].sum()

print("\n" + "=" * 50)
print(f"CORRIDOR ANALYSIS SUMMARY ({args.mode.upper()})")
print("=" * 50)
print(f"Total distance: {total_km:.1f} km")
print(f"Total time:     {fmt_hhmm(total_min)} ({total_min:.0f} minutes)")
print("\nSegment breakdown:")
for _, row in seg_summary.iterrows():
    print(f"  {row['segment_name']}: {row['distance_km']:.1f} km, {row['est_time_hh:mm']}")

print("\nOutput files:\n  • segment_stats.csv\n  • corridors_map.html\n  • corridors_clean.geojson")

# -----------------------
# 8. Tiny Flask server to view map
# -----------------------
app = Flask(__name__)

@app.route("/")
def show_map():
    return send_file("corridors_map.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

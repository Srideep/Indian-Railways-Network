"""
INDIAN VANDE BHARAT CORRIDORS – QUICK‑LOOK MAP
Libraries: geopandas · networkx · matplotlib · contextily · momepy · libpysal
"""

import contextily
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from contextily import add_basemap
import momepy as mm
from libpysal import weights
from itertools import pairwise
from collections import Counter

# ───────────────────────────── 1 · MASTER STATION TABLE ──────────────────────────
# (Hand‑curated decimal‑degree coordinates; tweak if you need higher precision)
STOPS = {
    # Delhi cluster
    "NDLS": ("New Delhi", 28.6392, 77.2158),
    "DLI": ("Delhi Jn", 28.6560, 77.2278),
    "ANVT": ("Anand Vihar Tml", 28.6509, 77.3146),
    "NZM": ("Hazrat Nizamuddin", 28.5905, 77.2507),

    # Punjab, Haryana, HP & J&K
    "ASR": ("Amritsar Jn", 31.6361, 74.8688),
    "BEAS": ("Beas", 31.5383, 75.3011),
    "JRC": ("Jalandhar Cantt", 31.3125, 75.6176),
    "PGW": ("Phagwara Jn", 31.2186, 75.7703),
    "LDH": ("Ludhiana Jn", 30.9120, 75.8542),
    "UMB": ("Ambala Cantt Jn", 30.3759, 76.7796),
    "CDG": ("Chandigarh", 30.7000, 76.7850),
    "ANSB": ("Anandpur Sahib", 31.2385, 76.5004),
    "UHL": ("Una Himachal", 31.4690, 76.2740),
    "AADR": ("Amb Andaura", 31.8028, 76.3297),
    "PTKC": ("Pathankot Cantt", 32.2643, 75.6534),
    "JAT": ("Jammu Tawi", 32.6894, 74.8656),
    "SVDK": ("SMVD Katra", 32.9908, 74.9314),
    "BAHL": ("Banihal", 33.4359, 75.1905),
    "SINA": ("Srinagar (Kashmir)", 34.0758, 74.8081),

    # Western UP / Uttarakhand
    "MTC": ("Meerut City", 29.0033, 77.6990),
    "HPU": ("Hapur", 28.7430, 77.7763),
    "TDL": ("Tundla Junction", 27.213522, 78.239075),
    "ETW": ("Etah", 27.5583, 78.6614),
    "MB": ("Moradabad", 28.8372, 78.7738),
    "BE": ("Bareilly", 28.3651, 79.4155),
    "DDN": ("Dehradun", 30.3246, 78.0286),
    "HW": ("Haridwar Jn", 29.9460, 78.1673),
    "RK": ("Roorkee", 29.8667, 77.8938),
    "SRE": ("Saharanpur", 29.9634, 77.5457),
    "DBD": ("Deoband", 29.6922, 77.6778),
    "MOZ": ("Muzaffarnagar", 29.4815, 77.7085),

    # Gangetic plain (UP / Bihar / Jharkhand)
    "CNB": ("Kanpur Central", 26.4515, 80.3312),
    "PRYJ": ("Prayagraj Jn", 25.4400, 81.8340),
    "BSB": ("Varanasi Jn", 25.3226, 82.9882),
    "LKO": ("Lucknow Charbagh", 26.8381, 80.9240),
    "BSBS": ("Banaras", 25.28472, 82.97222),
    "AY": ("Ayodhya Cantt", 26.7851, 82.1391),
    "KRJ": ("Khurja Jn", 28.2678, 77.8698),
    "ALJN": ("Aligarh Jn", 27.9002, 78.0716),
    "DDU": ("Pt DD Upadhyaya Jn", 25.2819, 83.1195),
    "SSM": ("Sasaram", 24.9649, 84.0360),
    "GAYA": ("Gaya Jn", 24.7969, 85.0033),
    "NWD": ("Nawadah", 24.8853, 85.5440),
    "KIUL": ("Kiul Jn", 25.1719, 86.0977),
    "JSME": ("Jasidih Jn", 24.5124, 86.6444),
    "DGHR": ("Deoghar", 24.4764, 86.7005),

    # Central / Bundelkhand
    "AGC": ("Agra Cantt", 27.1495, 78.0677),
    "GWL": ("Gwalior Jn", 26.2234, 78.1805),
    "DAA": ("Datia", 25.6724, 78.4567),
    "VGLJ": ("Jhansi Jn", 25.4482, 78.5609),
    "LAR": ("Lalitpur Jn", 24.2116, 78.2094),
    "TKMG": ("Tikamgarh", 24.7434, 78.8467),
    "MCSC": ("MCS Chhatarpur", 24.8958, 79.1142),
    "KURJ": ("Khajuraho", 24.8478, 79.9337),
}
STOPS.update({
    "GKP":  ("Gorakhpur Jn",        26.7598,   83.3818),   
    "BST":  ("Basti",              26.822845, 82.763443),  
    "RBL":  ("Rae Bareli Jn",       26.230299, 81.240891), 
    "LJN":  ("Lucknow Jct",         26.8320,  80.9190),    
    "NBD":  ("Najibabad Jn",        29.607981, 78.342674), 
    "CPJ":  ("Kaptanganj Jn",       26.926667, 83.715278), 
    "BUG":  ("Bagaha",             27.122196, 84.072235),  
    "NKE":  ("Narkatiaganj Jn",     27.108870, 84.468121), 
    "BTH":  ("Bettiah",            26.799999, 84.500000),  # Bettiah :contentReference[oaicite:8]{index=8}
    "SGL":  ("Sagauli Jn",          26.758700, 84.739300), # Sagauli :contentReference[oaicite:9]{index=9}
    "BMKI": ("Bapudham Motihari",   26.650000, 84.916664), # Motihari :contentReference[oaicite:10]{index=10}
    "MFP":  ("Muzaffarpur Jn",      26.122300, 85.377900), # Muzaffarpur :contentReference[oaicite:11]{index=11}
    "HJP":  ("Hajipur Jn",          25.683300, 85.216700), # Hajipur :contentReference[oaicite:12]{index=12}
    "PPTA": ("Patliputra Jn",       25.621620, 85.068870), # Patliputra :contentReference[oaicite:13]{index=13}
})
# ── append the missing North-Western Railway Vande Bharat stops ──
STOPS.update({
    "AII":  ("Ajmer Jn",           26.456986, 74.637664),   
    "KSG":  ("Kishangarh",         26.588528, 74.872513),   
    "GADJ": ("Gandhinagar Jaipur", 26.873471, 75.799008),   
    "AWR":  ("Alwar Jn",           27.560932, 76.625015),   
    "RE":   ("Rewari Jn",          28.183332, 76.616669),   
    "GGN":  ("Gurgaon",            28.489369, 77.010925),   
    "DEC":  ("Delhi Cantt",        28.599997, 77.133333),   
    "JP":   ("Jaipur Jn",          26.919769, 75.788369),   
    "JU":   ("Jodhpur Jn",         26.283997, 73.022506),   
    "PMY":  ("Pali Marwar",        25.790970, 73.327290),   
    "FA":   ("Falna",              25.235950, 73.235150),   
    "ABR":  ("Abu Road",           24.480000, 72.780000),   
    "PNU":  ("Palanpur Jn",        24.179331, 72.426682),   
    "MSH":  ("Mahesana Jn",        23.586761, 72.369949),   
    "SBIB": ("Sabarmati BG",       23.071457, 72.587237),   
    "UDZ":  ("Udaipur City",       24.571293, 73.691521),   
    "RPZ":  ("Rana Pratap Nagar",  24.582770, 73.728670),   
    "MVJ":  ("Mavli Jn",           24.783353, 73.987019),   
    "COR":  ("Chittaurgarh Jn",    24.873640, 74.623570),   
    "BHL":  ("Bhilwara",           25.346251, 74.636383),  
    "BJNR": ("Bijainagar",         25.926758, 74.650632),
    "CNA":  ("Chanderiya",         24.369190, 73.986610),
    'BUDI': ("Bundi",              25.437290, 75.645940),
    'KOTA': ("Kota Jn",            25.183333, 75.833333),
    'SWM':  ("Sawai Madhopur",     26.022500, 76.330000),
    'GGC':  ("Gangapur City",      26.490000, 76.710000),
})

# ───────────────────────────── 2 · ROUTE DEFINITIONS ─────────────────────────────
ROUTES = {
    # 1
    "Amritsar ⇄ Delhi Jn": ["ASR", "BEAS", "JRC", "PGW", "LDH", "UMB", "DLI"],
    # 2
    "New Delhi ⇄ Amb Andaura": ["NDLS", "UMB", "CDG", "ANSB", "UHL", "AADR"],
    # 3
    "New Delhi ⇄ SMVD Katra": ["NDLS", "UMB", "LDH", "PTKC", "JAT", "SVDK"],
    # 4
    "Meerut ⇄ Lucknow": ["MTC", "HPU", "MB", "BE", "LKO"],
    # 5
    "Anand Vihar ⇄ Ayodhya": ["ANVT", "KRJ", "ALJN", "CNB", "LKO", "AY"],
    # 6
    "Dehradun ⇄ Anand Vihar":
    ["DDN", "HW", "RK", "SRE", "DBD", "MOZ", "MTC", "ANVT"],
    # 7 (the one you already had)
    "New Delhi ⇄ Varanasi": ["NDLS", "CNB", "PRYJ", "BSB"],
    # 8
    "Nizamuddin ⇄ Khajuraho":
    ["NZM", "AGC", "GWL", "DAA", "VGLJ", "LAR", "TKMG", "MCSC", "KURJ"],
    # 9
    "Varanasi ⇄ Deoghar":
    ["BSB", "DDU", "SSM", "GAYA", "NWD", "KIUL", "JSME", "DGHR"],
    # 10
    "SVDK ⇄ Srinagar": ["SVDK", "BAHL", "SINA"],
    # 11
    "Agra Cantt ⇄ Banaras": ["AGC", "TDL", "ETW", "CNB", "PRYJ", "BSBS"],
    # 12
    "Gorakhpur ⇄ Prayagraj": ["GKP", "BST", "AY", "LKO", "RBL", "PRYJ"],
    # 13
    "Lucknow Jct ⇄ Dehradun": ["LJN", "BE", "MB", "NBD", "HW", "DDN"],
    # 14
    "Gorakhpur ⇄ Patliputra": ["GKP", "CPJ", "BUG", "NKE", "BTH", "SGL",
                                "BMKI", "MFP", "HJP", "PPTA"],
    # 15
    "Ajmer ⇄ Chandigarh": [
        "AII",   # Ajmer Jn
        "KSG",   # Kishangarh
        "JP",    # Jaipur Jn
        "GADJ",  # Gandhinagar Jaipur
        "AWR",   # Alwar Jn
        "RE",    # Rewari Jn
        "GGN",   # Gurgaon
        "DEC",   # Delhi Cantt
        "UMB",   # Ambala Cantt Jn
        "CDG",   # Chandigarh
    ],
    # 16
    "Jodhpur ⇄ Sabarmati": [
        "JU",    # Jodhpur Jn
        "PMY",   # Pali Marwar
        "FA",    # Falna
        "ABR",   # Abu Road
        "PNU",   # Palanpur Jn
        "MSH",   # Mahesana Jn
        "SBIB",  # Sabarmati BG
    ],
    # 17
    "Udaipur City ⇄ Jaipur": [
        "UDZ",   # Udaipur City
        "RPZ",   # Rana Pratap Nagar
        "MVJ",   # Mavli Jn
        "COR",   # Chittaurgarh Jn
        "BHL",   # Bhilwara
        "BJNR",  # Bijainagar
        "AII",   # Ajmer Jn
        "KSG",   # Kishangarh
        "JP",    # Jaipur Jn
    ],
    # 18
    "Udaipur City ⇄ Agra Cantonment": [
        "UDZ",   # Udaipur City
        "RPZ",   # Rana Pratap Nagar
        "MVJ",   # Mavli Jn
        "CNA",   # Chanderiya
        "BUDI",  # Bundi
        "KOTA",  # Kota Jn
        "SWM",   # Sawai Madhopur
        "GGC",   # Gangapur City
        "AGC",   # Agra Cantt
    ],
}

# ───────────────────────────── 3 · BUILD NODE & EDGE GDFS ────────────────────────
# 3a. Nodes
node_records = [
    dict(code=code, name=nm, lat=lat, lon=lon, geometry=Point(lon, lat))
    for code, (nm, lat, lon) in STOPS.items()
]
gdf_nodes = gpd.GeoDataFrame(node_records, crs="EPSG:4326")

# 3b. Edges
edge_rows = []
for route_name, stops in ROUTES.items():
    for u, v in pairwise(stops):
        pu = Point(STOPS[u][2], STOPS[u][1])  # (lon, lat)
        pv = Point(STOPS[v][2], STOPS[v][1])
        edge_rows.append(
            dict(u=u, v=v, route=route_name, geometry=LineString([pu, pv])))
gdf_edges = gpd.GeoDataFrame(edge_rows, crs="EPSG:4326")

# ───────────────────────── 5 · NETWORKX & TRANSFER DETECTION ─────────────────────
G = nx.DiGraph()
for _, n in gdf_nodes.iterrows():
    G.add_node(n.code, name=n.name)
for _, e in gdf_edges.iterrows():
    G.add_edge(e.u, e.v, route=e.route)

station_counts = Counter(
    s for r in ROUTES.values()
    for s in set(r))  # how many distinct routes touch each station

# ─────────────────────────────── 6 · PLOT ────────────────────────────────────────
cmap = plt.cm.get_cmap("tab20", len(ROUTES))  # up to 20 distinct colours
route_colors = {r: cmap(i) for i, r in enumerate(ROUTES)}

fig, ax = plt.subplots(figsize=(11, 13))

# 6a. Draw each route in its own colour
for route, color in route_colors.items():
    gdf_edges[gdf_edges.route == route].to_crs(3857).plot(ax=ax,
                                                          linewidth=3,
                                                          alpha=0.9,
                                                          color=color,
                                                          zorder=1,
                                                          label=route)

# 6b. Draw stations – squares for transfer points, circles otherwise
marker_styles = {
    True: dict(marker='s', color='white', edgecolors='black', linewidths=0.8),
    False: dict(marker='o', color='white', edgecolors='black', linewidths=0.8),
}
gdf_nodes_proj = gdf_nodes.to_crs(3857)
for _, row in gdf_nodes_proj.iterrows():
    is_transfer = station_counts[row.code] > 1
    gdf_nodes_proj.loc[[row.name]].plot(ax=ax,
                                        markersize=120 if is_transfer else 70,
                                        **marker_styles[is_transfer],
                                        zorder=2)
    ax.text(
        row.geometry.x + 5000,
        row.geometry.y + 5000,  # slight offset
        row.code,
        fontsize=7,
        va='bottom',
        ha='left')

# 6c. Basemap & legend
add_basemap(ax, source=contextily.providers.CartoDB.Positron)
ax.set_axis_off()
ax.legend(loc='upper right',
          fontsize=11,
          frameon=False,
          title="Vande Bharat Routes")
plt.tight_layout()
plt.savefig("VB_NorthernRailways.png", dpi=300)

# ───────────────────────── 7 · OPTIONAL SPATIAL WEIGHTS ──────────────────────────
# Example: 1‑NN weights for catchment modelling
w_knn = weights.KNN.from_dataframe(gdf_nodes, k=1)


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
import pandas as pd
import json
import os
# Route data


# Map specifications
map_specs = {
    "map_title": "Premium Express Network (Rajdhani, Duronto & Humsafar)",
    "rajdhani_route_color": "#CC0000",
    "duronto_route_color": "#228B22",
    "humsafar_route_color": "#FF6600",
    "route_line_width": 2,
    "station_marker_color": "#FFA500",
    "station_marker_size": 50,
    "major_city_label_size": 12,
    "map_background_color": "#F0F0F0",
    "include_scale_bar": True,
    "include_north_arrow": True,
    "additional_elements": {
        "legend_position": "lower right",
        "grid_lines": False
    },
    "output_file_name": "../media/premium_express_routes_map.png",
    "output_dpi": 500
}

# Load Rajdhani routes
rajdhani_filename = '../data/rajdhani_route_data.json'
try:    
    with open(rajdhani_filename, 'r', encoding='utf-8') as file:
        raw_data = json.load(file)
        rajdhani_route_data = raw_data['rajdhani_express_routes']
    print(f"✅ Successfully loaded {len(rajdhani_route_data['routes'])} Rajdhani routes from {rajdhani_filename}")
except FileNotFoundError:
    print(f"❌ Error: File {rajdhani_filename} not found")
    raise
except json.JSONDecodeError as e:
    print(f"❌ Error: Invalid JSON in '{rajdhani_filename}': {e}")
    raise

# Load Duronto routes
duronto_filename = '../data/duronto_route_data.json'
try:    
    with open(duronto_filename, 'r', encoding='utf-8') as file:
        raw_data = json.load(file)
        duronto_route_data = raw_data['duronto_express_routes']
    print(f"✅ Successfully loaded {len(duronto_route_data['routes'])} Duronto routes from {duronto_filename}")
except FileNotFoundError:
    print(f"❌ Error: File {duronto_filename} not found")
    raise
except json.JSONDecodeError as e:
    print(f"❌ Error: Invalid JSON in '{duronto_filename}': {e}")
    raise

# Load Humsafar routes
humsafar_filename = '../data/humsafar_route_data.json'
try:    
    with open(humsafar_filename, 'r', encoding='utf-8') as file:
        raw_data = json.load(file)
        humsafar_route_data = raw_data['humsafar_express_routes']
    print(f"✅ Successfully loaded {len(humsafar_route_data['routes'])} Humsafar routes from {humsafar_filename}")
except FileNotFoundError:
    print(f"❌ Error: File {humsafar_filename} not found")
    raise
except json.JSONDecodeError as e:
    print(f"❌ Error: Invalid JSON in '{humsafar_filename}': {e}")
    raise

# Step 1: Preprocess the data
# Create lists to store station and route data
stations_data = []
routes_data = []

# Process Rajdhani routes
for route in rajdhani_route_data["routes"]:
    route_name = route["name"]
    route_status = route["status"]
    route_type = "Rajdhani"

    # Collect stations
    route_stations = []
    for station in route["stations"]:
        stations_data.append({
            'name': station['name'],
            'geometry': Point(station['lon'], station['lat']),
            'route': route_name,
            'status': route_status,
            'type': route_type
        })
        route_stations.append(Point(station['lon'], station['lat']))

    # Create LineString for the route
    if len(route_stations) > 1:
        routes_data.append({
            'name': route_name,
            'status': route_status,
            'type': route_type,
            'geometry': LineString([(p.x, p.y) for p in route_stations])
        })

# Process Duronto routes
for route in duronto_route_data["routes"]:
    route_name = route["name"]
    route_status = route["status"]
    route_type = "Duronto"

    # Collect stations
    route_stations = []
    for station in route["stations"]:
        stations_data.append({
            'name': station['name'],
            'geometry': Point(station['lon'], station['lat']),
            'route': route_name,
            'status': route_status,
            'type': route_type
        })
        route_stations.append(Point(station['lon'], station['lat']))

    # Create LineString for the route
    if len(route_stations) > 1:
        routes_data.append({
            'name': route_name,
            'status': route_status,
            'type': route_type,
            'geometry': LineString([(p.x, p.y) for p in route_stations])
        })

# Process Humsafar routes
for route in humsafar_route_data["routes"]:
    route_name = route["name"]
    route_status = route["status"]
    route_type = "Humsafar"

    # Collect stations
    route_stations = []
    for station in route["stations"]:
        stations_data.append({
            'name': station['name'],
            'geometry': Point(station['lon'], station['lat']),
            'route': route_name,
            'status': route_status,
            'type': route_type
        })
        route_stations.append(Point(station['lon'], station['lat']))

    # Create LineString for the route
    if len(route_stations) > 1:
        routes_data.append({
            'name': route_name,
            'status': route_status,
            'type': route_type,
            'geometry': LineString([(p.x, p.y) for p in route_stations])
        })

# Create GeoDataFrames
stations_gdf = gpd.GeoDataFrame(stations_data, crs='EPSG:4326')
routes_gdf = gpd.GeoDataFrame(routes_data, crs='EPSG:4326')

# Step 2: Create the base map and convert to Web Mercator
stations_gdf = stations_gdf.to_crs('EPSG:3857')
routes_gdf = routes_gdf.to_crs('EPSG:3857')

# Step 3: Create the map
fig, ax = plt.subplots(1, 1, figsize=(15, 12))
ax.set_facecolor(map_specs["map_background_color"])

# Add basemap
try:
    # Get bounds for India region
    bounds = stations_gdf.total_bounds
    # Add some padding
    padding = 200000  # meters
    ax.set_xlim(bounds[0] - padding, bounds[2] + padding)
    ax.set_ylim(bounds[1] - padding, bounds[3] + padding)

    # Add contextily basemap
    contextily.add_basemap(ax, crs=stations_gdf.crs, source=contextily.providers.CartoDB.Positron, alpha=0.7)
except:
    print("Could not load basemap, continuing without it...")

# Step 4: Plot routes by type
rajdhani_routes = routes_gdf[routes_gdf['type'] == 'Rajdhani']
duronto_routes = routes_gdf[routes_gdf['type'] == 'Duronto']
humsafar_routes = routes_gdf[routes_gdf['type'] == 'Humsafar']

# Plot Rajdhani routes
if not rajdhani_routes.empty:
    rajdhani_routes.plot(ax=ax, 
                        color=map_specs["rajdhani_route_color"], 
                        linewidth=map_specs["route_line_width"],
                        zorder=2)

# Plot Duronto routes
if not duronto_routes.empty:
    duronto_routes.plot(ax=ax, 
                       color=map_specs["duronto_route_color"], 
                       linewidth=map_specs["route_line_width"],
                       zorder=2)

# Plot Humsafar routes
if not humsafar_routes.empty:
    humsafar_routes.plot(ax=ax, 
                        color=map_specs["humsafar_route_color"], 
                        linewidth=map_specs["route_line_width"],
                        zorder=2)

# Plot stations
stations_gdf.plot(ax=ax, 
                 color=map_specs["station_marker_color"],
                 markersize=map_specs["station_marker_size"],
                 label='Stations',
                 zorder=3,
                 edgecolors='black',
                 linewidth=0.5)

# Step 5: Add labels for major cities
major_cities = [
    'New Delhi',
    'Mumbai',
    'Chennai',
    'Ahmedabad',
    'Varanasi',
    'Bengaluru',
    'Howrah',
    'Bhubaneswar',
    'Pune',
    'Lucknow',
    'Chandigarh',
    'Jaipur',
    'Amritsar',
    'Patna',
    'Puri',
    'Visakhapatnam',
    'Hyderabad',
    'Mumbai Central',
    'Hazrat Nizamuddin',
    'Secunderabad Jn',
    'Yesvantpur Jn',
    'Ernakulam Jn',
    'Jammu Tawi',
    'Sealdah',
    'Tirupati'
]
for idx, row in stations_gdf.iterrows():
    if row['name'] in major_cities:
        ax.annotate(row['name'], 
                   xy=(row.geometry.x, row.geometry.y),
                   xytext=(5, 5), 
                   textcoords='offset points',
                   fontsize=map_specs["major_city_label_size"],
                   fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                   zorder=4)

# Step 6: Style and customize the map
ax.set_title(map_specs["map_title"], fontsize=16, fontweight='bold', pad=20)

# Create custom legend
from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], color=map_specs["rajdhani_route_color"], lw=map_specs["route_line_width"], label='Rajdhani Express'),
    Line2D([0], [0], color=map_specs["duronto_route_color"], lw=map_specs["route_line_width"], label='Duronto Express'),
    Line2D([0], [0], color=map_specs["humsafar_route_color"], lw=map_specs["route_line_width"], label='Humsafar Express'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=map_specs["station_marker_color"], 
           markersize=8, label='Stations', markeredgecolor='black')
]

ax.legend(handles=legend_elements, loc=map_specs["additional_elements"]["legend_position"], 
         frameon=True, fancybox=True, shadow=True)

# Remove axis ticks and labels for cleaner look
ax.set_xlabel('')
ax.set_ylabel('')
ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# Add a simple north arrow
ax.annotate('N', xy=(0.95, 0.95), xycoords='axes fraction',
           fontsize=14, fontweight='bold',
           ha='center', va='center',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
ax.annotate('↑', xy=(0.95, 0.92), xycoords='axes fraction',
           fontsize=16, ha='center', va='center')

# Step 7: Save and display
plt.tight_layout()
plt.savefig(map_specs["output_file_name"], dpi=map_specs["output_dpi"], bbox_inches='tight', 
           facecolor='white', edgecolor='none')

print(f"Map saved as {map_specs['output_file_name']}")

# Print summary statistics
print(f"\n📊 Route Summary:")
print(f"   • Rajdhani Express: {len(rajdhani_routes)} routes")
print(f"   • Duronto Express: {len(duronto_routes)} routes") 
print(f"   • Humsafar Express: {len(humsafar_routes)} routes")
print(f"   • Total Stations: {len(stations_gdf)} unique stations")
print(f"   • Total Routes: {len(routes_gdf)} routes")

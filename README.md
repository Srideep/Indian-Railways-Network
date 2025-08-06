
# Indian Railway Network Visualization & Analysis

A comprehensive Python-based system for visualizing and analyzing major railway networks across India, including Vande Bharat Express, Rajdhani Express, Shatabdi Express, and Jan Shatabdi Express routes.

## 🚄 Overview

This project creates interactive maps and performs network analysis of India's premium railway services, providing insights into route connectivity, station importance, and geographic coverage across the country.

## 📊 Supported Railway Networks

### 1. **Vande Bharat Express** (`VB_Network.py`)
- India's fastest semi-high speed trains
- 70+ routes covering major cities from Kashmir to Kerala
- Color-coded route visualization with station markers

### 2. **Rajdhani Express** (`Rajdhani_Network.py`) 
- Premium long-distance trains connecting New Delhi with state capitals
- 25 routes with fully air-conditioned coaches
- Priority network analysis

### 3. **Shatabdi Express** (`Shatabdi_Network.py`)
- Day trains with premium amenities
- 21 routes for same-day return travel
- Maximum speeds up to 150 km/h

### 4. **Jan Shatabdi Express** (`Shatabdi_Network.py`)
- Affordable day trains for common passengers
- 23 routes with both AC and non-AC coaches
- Cost-effective premium travel option

### 5. **Northern Railways Focus** (`VB_NorthernRailways.py`)
- Specialized network analysis for Northern India
- Transfer station detection and route optimization
- NetworkX-based connectivity analysis

## 🗂️ Project Structure

```
├── data/                          # Route data in JSON format
│   ├── vb_route_data.json        # Vande Bharat routes
│   ├── rajdhani_route_data.json  # Rajdhani routes  
│   ├── Shatabdi_route_data.json  # Shatabdi & Jan Shatabdi routes
│   └── segment_stats.csv         # Analysis statistics
├── src/                          # Python visualization scripts
│   ├── VB_Network.py            # Vande Bharat network
│   ├── Rajdhani_Network.py      # Rajdhani network
│   ├── Shatabdi_Network.py      # Shatabdi networks
│   └── VB_NorthernRailways.py   # Northern Railways analysis
├── media/                        # Generated maps and visualizations
└── requirements.txt              # Python dependencies
```

## 🛠️ Technology Stack

- **GeoPandas** - Geospatial data processing and analysis
- **Matplotlib** - Map generation and visualization
- **Contextily** - Basemap integration (CartoDB, OpenStreetMap)
- **NetworkX** - Network analysis and graph theory
- **Shapely** - Geometric operations
- **Pandas** - Data manipulation and statistics

## 🚀 Getting Started

### Prerequisites

All dependencies are automatically managed in the Replit environment. The key libraries include:

```
plotly
pandas  
geopandas
shapely
contextily
networkx
matplotlib
```

### Running the Visualizations

1. **Generate Vande Bharat Network Map:**
   ```bash
   cd src && python VB_Network.py
   ```

2. **Generate Rajdhani Network Map:**
   ```bash
   cd src && python Rajdhani_Network.py
   ```

3. **Generate Shatabdi Networks:**
   ```bash
   cd src && python Shatabdi_Network.py
   ```

4. **Northern Railways Analysis:**
   ```bash
   cd src && python VB_NorthernRailways.py
   ```

## 📈 Features

### 🗺️ **Interactive Mapping**
- High-resolution PNG exports (500+ DPI)
- Contextual basemaps with geographic context
- Color-coded routes by train type/status
- Station markers with major city labels
- North arrows and professional styling

### 🔍 **Network Analysis**
- Route connectivity analysis
- Transfer station identification  
- Geographic coverage statistics
- Distance and travel time calculations
- Station importance ranking

### 📊 **Data Processing**
- GeoJSON route data loading
- Coordinate system transformations (WGS84 → Web Mercator)
- Statistical analysis and CSV export
- Error handling and data validation

## 🎯 Key Insights

### Geographic Coverage
- **Vande Bharat**: Pan-India coverage with focus on major economic corridors
- **Rajdhani**: Hub-and-spoke model centered on New Delhi
- **Shatabdi**: Regional day-train connectivity
- **Jan Shatabdi**: Affordable regional connectivity

### Network Characteristics
- **Route Density**: Highest in Golden Quadrilateral corridor
- **Transfer Hubs**: Delhi, Mumbai, Chennai, Kolkata as major nodes
- **Speed Profiles**: Vande Bharat (160km/h) > Shatabdi (150km/h) > Rajdhani (140km/h)

## 🔧 Customization

### Map Styling
Modify the `map_specs` dictionary in each script to customize:
- Colors and line widths
- Output resolution and format
- Background styles and themes
- Label fonts and positioning

### Data Sources
Update JSON files in `/data/` to add new routes or modify existing ones:
- Station coordinates (latitude/longitude)
- Route names and train numbers
- Service status (current/prospective)
- Frequency and speed data

## 📸 Sample Outputs

The system generates professional-quality railway network maps saved in `/media/`:
- `vande_bharat_routes_map.png` - Complete VB network
- `rajdhani_exp_routes_map.png` - Rajdhani network  
- `Jan_Shatabdi_exp_routes_map.png` - Jan Shatabdi routes
- `VB_NorthernRailways.png` - Northern railways analysis

## 🤝 Contributing

To extend the project:
1. Add new route data to appropriate JSON files
2. Create new visualization scripts following existing patterns
3. Update this README with new features
4. Test map generation and data processing

## 📝 Data Sources

Route and station data compiled from:
- Indian Railways official timetables
- Ministry of Railways press releases  
- Railway zone-wise route maps
- Station coordinate databases

---

**Built with ❤️ for Indian Railways enthusiasts and transport planners**

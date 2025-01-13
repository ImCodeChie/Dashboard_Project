# 🌳 Forest Fire Analytical Dashboard

This repository contains the **Forest Fire Analytical Dashboard**, a comprehensive data visualization and analysis tool. The application leverages Python libraries such as Dash, Plotly, GeoPandas, and Pandas to explore forest fire data. The dashboard provides insights into forest fires in the Bouches-du-Rhône region of France, showcasing trends, spatial distributions, and more.

---

## 🎥 Demo
Click on the link below to see a short video of the dashboard:
```markdown
[![Watch the demo](https://streamable.com/2zqjvw)
```
---

## 📋 Features
1. **Home Page**:
   - Aggregated summaries of forest fire data.
   - A bar chart showcasing the total burned area by commune.

2. **Insights Page**:
   - Pie charts for fire origin distribution.
   - Bubble charts depicting occurrences by DFCI codes.
   - Interactive choropleth maps of population intensity.

3. **Trends Page**:
   - Line charts for monthly fire trends.
   - Hourly and yearly trend analysis using bar charts.

4. **QGIS Mapping Page**:
   - Seamlessly embed and view QGIS-generated maps.

5. **Interactive Sidebar**:
   - Navigate pages and apply filters for personalized visualizations.
   - Detailed documentation and sources are available.

---

## 🛠️ Installation and Setup

### Prerequisites
- Python 3.7 or later
- Required Python libraries (see `requirements.txt`)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/forest-fire-dashboard.git
   cd forest-fire-dashboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open the browser and visit:
   ```
   http://127.0.0.1:8050/
   ```

---

## 📂 File Structure
```
forest-fire-dashboard/
│
├── app.py                   # Main application logic
├── requirements.txt         # Dependencies for the project
├── assets/                  # Static assets
│   ├── styles.css           # Custom CSS styles
│   ├── wildfire.webp        # Background image
│   └── LOGO_AMU.png         # Project logo
├── data/                    # Input data files (CSV, shapefiles)
│   ├── Classeur1.csv        # Forest fire dataset
│   └── Commune_BR_13.shp    # Shapefile for spatial analysis
├── geojson/                 # Exported GeoJSON files
│   └── all_communes.geojson # GeoJSON for visualization
├── templates/               # HTML templates for embedding maps (qgis2web_2024_11_06-12_39_04_012529)
│   └── index.html           # Example QGIS export
├── README.md                # Documentation
└── LICENSE                  # License file
```

---

## 📊 Data Pipeline Overview

### 1. **Load Data**
- The primary dataset (`Classeur1.csv`) is read using Pandas, handling various encodings and skipping invalid lines.
- Forest fire records are filtered to include only the Bouches-du-Rhône region (INSEE Code starts with `13`) for the years 1973–2024.
- Shapefile data (`Commune_BR_13.shp`) is loaded using GeoPandas for spatial analysis.

### 2. **Data Cleaning**
- Strip extra spaces in column names and content.
- Convert dates to `datetime` objects and enforce consistent data types.
- Remove rows and columns with missing or invalid values.

### 3. **Data Merging**
- Shapefile and CSV data are merged on the `Code INSEE` field.
- Rows with invalid geometries are filtered out.
- Reproject spatial data to EPSG:4326 for web mapping compatibility.

### 4. **GeoJSON Export**
- The cleaned and merged data is exported as a GeoJSON file for easy use in dashboards and maps.

---

---

## 🔍 Code Explanation
The code for data loading, cleaning, and merging is as follows:

```python
import pandas as pd
import geopandas as gpd

# Load CSV data
df = pd.read_csv('Classeur1.csv', encoding='ISO-8859-1', delimiter=';', on_bad_lines='skip')
df = df[df['Code INSEE'].str[:2] == '13']  # Filter for Department '13'

# Clean data
df['Alerte'] = pd.to_datetime(df['Alerte'], errors='coerce')
df = df.dropna(how='any')  # Drop rows with NaN values

# Load shapefile
gdf = gpd.read_file("shapefile/Commune_BR_13.shp")
gdf = gdf.to_crs(epsg=4326)  # Reproject to EPSG:4326

# Merge data
merged = gdf.merge(df, how='left', left_on='INSEE_COM', right_on='Code INSEE')
merged = merged[merged.is_valid & ~merged.geometry.is_empty]

# Export to GeoJSON
merged.to_file("geojson/all_communes.geojson", driver='GeoJSON')
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---

Let me know if you need help with additional sections or edits!

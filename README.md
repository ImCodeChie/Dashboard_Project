# 🌳 Forest Fire Analytical Dashboard

This repository contains the **Forest Fire Analytical Dashboard**, a comprehensive data visualization and analysis tool. The application leverages Python libraries such as Dash, Plotly, GeoPandas, and Pandas to explore forest fire data. The dashboard provides insights into forest fires in the Bouches-du-Rhône region of France, showcasing trends, spatial distributions, and more.

---

## 🎥 Demo
Click on the link below to see a short video of the dashboard:
```markdown
https://drive.google.com/file/d/1ORp9lyQBh5qhIiAkhT1Z_NaMdlO4Baqe/view?usp=drive_link

```

![Alt text](https://github.com/ImCodeChie/Dashboard_Project/blob/6b8bfb85be8d7e60eb68ccb71df0be3e69d20fcf/Home.PNG)

![Alt text](https://github.com/ImCodeChie/Dashboard_Project/blob/b3e98daf34235e35529cbc98bb3fef2c1585d899/Insights.PNG)

![Alt text](https://github.com/ImCodeChie/Dashboard_Project/blob/a2c68d148d19295278e4cefdc9a2bdccd2733b69/Temporal%20Trends.PNG)

![Alt text](https://github.com/ImCodeChie/Dashboard_Project/blob/9779f2a798df00a9a5c07f2d1455a70b9d61041e/QGIS.PNG)


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

-------------------------------------------------------------------------------------------------------
```
# Dash App Initialization

The app is initialized using Dash:
app = dash.Dash(__name__, external_stylesheets=['/assets/styles.css'], suppress_callback_exceptions=True)
server = app.server

An external stylesheet (styles.css) is linked to the app for custom styling.
The app is set up to serve HTML content from the html_file_directory via the @app.server.route('/html/<path:path>') decorator.

```

```
# Sidebar Components
The sidebar contains interactive elements like dropdowns and navigation links:
sidebar = html.Div([ ... ])
Dropdowns allow users to filter fire data by year and commune.
The navigation links guide the user to different sections of the dashboard, including the Home, Insights, Trends, and QGIS Mapping layouts.
A toggle button allows the sidebar to be hidden or shown.

```
```
# Home Layout
The home layout (home_layout) displays key statistics (e.g., max fires, total area burned) and a bar chart:

home_layout = html.Div([ ... ])
The statistics are dynamically updated using Dash callbacks. The bar chart visualizes the total area burned by each commune.
The layout contains multiple cards that display the statistical information for easy visualization.
```
```
# Insights Layout
The insights layout (insights_layout) contains a combination of charts, including:
Pie Chart: Visualizes fire origin distribution.
Bubble Chart: Displays fire occurrences by DFCI code with varying bubble sizes based on fire impact.
Choropleth Map: Shows the population density of communes in the Bouches-du-Rhône region using a color scale.
These visualizations are updated based on the user's selection of year and commune via Dash callbacks.
```

```
# Trends Layout
The trends layout (trends_layout) contains time-based trend charts:
Monthly Trend Chart: Displays fire alerts by month.
Hourly Trend Chart: Shows fire alerts by hour.
Yearly Trend Chart: Visualizes fire alerts by year.
These charts are updated dynamically based on the selected year using Dash callbacks.
```

```
# QGIS Mapping Layout
The QGIS layout (qgis_mapping_layout) embeds a QGIS-generated HTML map:

html.Iframe(src='/html/index.html', width="100%", height="100%")
This map displays the fire data geographically, allowing users to explore spatial patterns.
```

```
# Callbacks
Dash callbacks are used extensively to update the dashboard's visualizations and data based on user input (e.g., year and commune selections).
The update_data_summaries function updates key statistics such as max fires, total area burned, etc.
The update_bar_chart function updates the bar chart based on selected filters.
The update_insights function updates the pie chart, bubble chart, and choropleth map based on user selections.
The update_trends function updates the trend charts (monthly, hourly, yearly) based on the selected year.
```

```
# Toggle Sidebar
The sidebar can be toggled to show or hide using the button:

toggle_button = html.Button("▶️", id='toggle-sidebar', className='toggle-button')
A callback function (toggle_hidden_sidebar) manages the sidebar visibility when the toggle button is clicked.
```

```
# Main Layout
The app layout includes the sidebar, content area, and navigation:

app.layout = html.Div([ ... ])
The layout dynamically updates to display different pages (home, trends, insights, QGIS mapping) based on the current URL path.
dcc.Location(id='url', refresh=False) tracks the current URL and updates the page content accordingly.
```

```
# Running the App
Finally, the app is run with:

app.run_server(debug=True, port=8050)
The app runs on port 8050, and you can access it locally in your browser.
```








# 🧑‍💻 Authors and Acknowledgments
This project was developed as part of the Geovisualization course at University of Aix-Marseille. The authors would like to acknowledge:

Course Instructors and Mentors: For providing guidance and insights during the development of this project.
Data Source: Défense de la Forêt Contre les Incendies (DFCI) for providing the fire-related datasets used in this analysis.
The CSS portion of the project has been developed to improve the app’s layout and styling. However, the responsivity of the application needs further refinement. If time allows, this will be completed in the future to ensure the app is fully responsive and provides a seamless experience across different devices and screen sizes.

Current Status:
The app's code is ready, with functionality for data visualization and interaction fully implemented.
CSS code is ready, responsivity improvements are planned to be completed when there is enough time.

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---

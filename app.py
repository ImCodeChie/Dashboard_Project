import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import geopandas as gpd
import dash_bootstrap_components as dbc
import unidecode
import plotly.graph_objects as go

# --- Data Loading ---
# Load CSV Data
try:
    df = pd.read_csv('Classeur1.csv', encoding='ISO-8859-1', delimiter=';', on_bad_lines='skip')
except UnicodeDecodeError:
    df = pd.read_csv('Classeur1.csv', encoding='latin1', delimiter=';', on_bad_lines='skip')


# Clean column names and types
df.columns = df.columns.str.strip()
df['Alerte'] = pd.to_datetime(df['Alerte'], errors='coerce')
df['Code INSEE'] = df['Code INSEE'].astype(str).str.strip()

# Filter CSV by year range (2018–2024)
df = df[(df['Alerte'].dt.year >= 1970) & (df['Alerte'].dt.year <= 2024)]

# Drop rows with NaN values in any column
df = df.dropna(how='any')  # Removes rows with NaN in any column

# Drop columns that contain all NaN values
df = df.dropna(axis=1, how='all')  # Removes columns with all NaN values

print(df)
print(df.columns)


import geopandas as gpd
import pandas as pd

# -------------------------------
# 1. Load Shapefile
# -------------------------------
shapefile_path = "C:/Users/Lutfi/Desktop/Forest Fire Project/Dashboard_Project/shapefile/Commune_BR_13.shp"
# shapefile_path = "/shapefile/Commune_BR_13.shp"
gdf = gpd.read_file(shapefile_path)

print("✅ Shapefile loaded successfully.")
print(gdf.head())

# Clean shapefile data
gdf.columns = gdf.columns.str.strip()
gdf['INSEE_COM'] = gdf['INSEE_COM'].astype(str).str.strip()
gdf['NOM_DEPT'] = gdf['NOM_DEPT'].astype(str).str.strip()

# -------------------------------
# 2. Filter for Bouches-du-Rhône
# # -------------------------------
# if 'NOM_DEPT' not in gdf.columns:
#     raise ValueError("'NOM_DEPT' column not found in shapefile.")

# gdf = gdf[gdf['NOM_DEPT'] == 'Bouches-du-Rhône']

# gdf = gdf[gdf['CODE_DEPT'] == 13]

# if gdf.empty:
#     raise ValueError("No data left after filtering by 'NOM_DEPT'. Check your shapefile data!")

# print(f"✅ Filtered Shapefile has {len(gdf)} rows.")

# -------------------------------
# 3. Load CSV and Prepare for Merge
# -------------------------------


print("✅ CSV loaded successfully.")
print(df.head())

# Ensure 'Code INSEE' exists and clean it
if 'Code INSEE' not in df.columns:
    raise ValueError("'Code INSEE' column not found in CSV file.")

df['Code INSEE'] = df['Code INSEE'].astype(str).str.strip()

# Check common keys
common_insee = set(gdf['INSEE_COM']) & set(df['Code INSEE'])
print(f"✅ Number of common INSEE codes: {len(common_insee)}")

if len(common_insee) == 0:
    raise ValueError("No common INSEE codes found between shapefile and CSV!")

# -------------------------------
# 4. Merge Shapefile and CSV
# -------------------------------
merged = gdf.merge(df, how='left', left_on='INSEE_COM', right_on='Code INSEE')

# Drop rows with null geometries or missing values in critical fields
# merged = merged.dropna(subset=['surf_ha', 'geometry'])

# Ensure 'surf_ha' is numeric
# merged['surf_ha'] = pd.to_numeric(merged['surf_ha'], errors='coerce')
# merged = merged.dropna(subset=['surf_ha'])

print(f"✅ Merged GeoDataFrame has {len(merged)} rows after dropping null geometries and values.")

# -------------------------------
# 5. Validate Geometries
# -------------------------------
invalid_geometries = merged[~merged.is_valid]
if not invalid_geometries.empty:
    print(f"⚠️ Found {len(invalid_geometries)} invalid geometries. These will be ignored.")
merged = merged[merged.is_valid]

# Ensure no empty geometries
merged = merged[~merged.geometry.is_empty]

if merged.empty:
    raise ValueError("Merged GeoDataFrame is empty after filtering valid geometries!")

# -------------------------------
# 6. Set CRS and Reproject
# -------------------------------
if merged.crs is None:
    merged = merged.set_crs(epsg=2154)  # Assuming original CRS
merged = merged.to_crs(epsg=4326)

print("✅ CRS reprojected to EPSG:4326.")

# -------------------------------
# 7. Export to GeoJSON
# -------------------------------
geojson_file_path = "C:/Users/Lutfi/Desktop/Forest Fire Project/Dashboard_Project/geojson/all_communes.geojson"
merged.to_file(geojson_file_path, driver='GeoJSON')

print(f"✅ GeoJSON successfully created at {geojson_file_path}")
print(f"✅ Number of features in GeoJSON: {len(merged)}")

# -------------------------------
# 8. Final Validation Output
# -------------------------------
# Filter the GeoDataFrame by CODE_DEPT == 13 (Bouches-du-Rhône)
# merged = merged[merged['CODE_DEPT'] == 13]

print(merged[['INSEE_COM', 'Code INSEE', 'surf_ha']].head())






# --- Dash App Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Forest Fire Analytical Dashboard"
server = app.server



from flask import send_from_directory
# Set the path to the directory containing the HTML file
html_file_directory = r'C:\Users\Lutfi\Desktop\Forest Fire Project\Dashboard_Project\qgis2web_2024_11_06-12_39_04_012529'

# Flask route to serve the HTML file
@app.server.route('/html/<path:path>')
def serve_html(path):
    return send_from_directory(html_file_directory, path)


# --- Sidebar Components ---Fire🔥
# --- Sidebar Components ---Fire🔥
# --- Sidebar Components ---Fire🔥
sidebar = html.Div([
    html.H1("Forest Fire Analytical Dashboard", style={
        'textAlign': 'left', 'color': '#fff', 'fontSize': '44px',
        'marginBottom': '30px', 'fontWeight': 'bold'
    }),
    html.Label("Select Year", style={'color': '#fff'}),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': str(year), 'value': year} for year in df['Alerte'].dt.year.dropna().unique()],
        placeholder="Select a Year",
        style={'marginBottom': '20px'}
    ),
    html.Label("Select Commune", style={'color': '#fff'}),
    dcc.Dropdown(
        id='commune-dropdown',
        options=[{'label': commune, 'value': commune} for commune in df['Commune'].unique()],
        placeholder="Select a Commune",  # Placeholder text
        style={'marginBottom': '20px'}
    ),
    html.Hr(style={'borderColor': '#fff'}),
    dbc.Nav([
        dbc.NavLink("🏠 Home", href='/', active='exact'),
        dbc.NavLink("📊 Insights", href='/insights', active='exact'),
        dbc.NavLink("📈 Trends", href='/trends', active='exact'),
        dbc.NavLink("🗺️ QGIS Mapping", href='/qgis_mapping', active='exact'),
    ], vertical=True, pills=True, style={'marginTop': '20px'}),

    html.Div([
        html.Img(src="/assets/LOGO_AMU.png", height="70px"),
        html.P("Data Sources: French Government & Fire Data", style={'fontSize': '12px', 'color': '#fff'})
    ], style={'position': 'absolute', 'bottom': '5px', 'left': '10px', 'textAlign': 'center'})
], id='main-sidebar', style={
    'position': 'fixed', 'top': 0, 'left': 0, 'height': '100vh', 'width': '265px',
    'backgroundColor': '#002855', 'padding': '20px', 'zIndex': 1000, 'transition': '0.3s'
})

# --- Toggle Button with Dynamic Icons ---
toggle_button = html.Button(
    "⏩",  # Sidebar(01) Icon
    id='toggle-sidebar',
    style={
        'position': 'fixed',
        'top': '50%',
        'left': '245px',
        'transform': 'translateY(-50%)',
        'backgroundColor': '#f8f9fa',
        'border': '1px solid #ccc',
        'borderRadius': '50%',
        'width': '40px',
        'height': '40px',
        'textAlign': 'center',
        'zIndex': 1002,
        'cursor': 'pointer'
    }
)

# --- Hidden Sidebar for Key Info ---
hidden_sidebar = html.Div([
    html.H3("🔑 Key Information", style={'textAlign': 'center', 'marginBottom': '20px'}),
    html.P("This dashboard visualizes forest fire data in the Bouches-du-Rhône region from 2018 to 2024."),
    html.P("Key insights include total fires, affected area, and time-based trends."),
    html.P("Use the navigation menu to switch between views."),
], id='hidden-sidebar', style={
    'position': 'fixed', 'top': 0, 'left': '265px', 'width': '295px', 'height': '100vh',
    'backgroundColor': '#f8f9fa', 'padding': '20px', 'display': 'none', 'zIndex': '1001', 'transition': '0.3s'
})

# --- Toggle Button with Dynamic Icons ---
toggle_button = html.Button(
    "⏩",  # Sidebar(01) Icon
    id='toggle-sidebar',
    style={
        'position': 'fixed',
        'top': '50%',
        'left': '245px',
        'transform': 'translateY(-50%)',
        'backgroundColor': '#f8f9fa',
        'border': '1px solid #ccc',
        'borderRadius': '50%',
        'width': '40px',
        'height': '40px',
        'textAlign': 'center',
        'zIndex': 1002,
        'cursor': 'pointer'
    }
)


# --- Home Layout ---
# --- Home Layout --- 
home_layout = html.Div([
    sidebar,  # Sidebar remains fixed
    toggle_button,  # Toggle button for sidebar visibility
    hidden_sidebar,  # Hidden sidebar for key information

    # Title with solid background
    html.Div([
        html.H1("Bouches-du-Rhône Department of France", style={
            'textAlign': 'left',
            'color': '#002855',  # White text color for contrast
            'fontSize': '26px',  # Font size of the title
            'fontWeight': 'bold',
            'padding': '10px',
            'margin': '0',  # Remove all default margin
            'boxSizing': 'border-box'
        }),
    ], style={
        'backgroundColor': '#bd4343',  # Solid background color (you can change this)
        'width': '100%',
        'position': 'relative',  # Ensures the title is above other sections
        'zIndex': '2',  # Makes sure it's on top
        'boxShadow': '0px 0px 0px rgba(0, 0, 0, 0)',  # Optional: Add a slight shadow for aesthetics
        'paddingLeft': '265px',
        'overflow': 'hidden',  # Prevents any content overflow
        'boxSizing': 'border-box'
    }),

    html.Div([
        # Data Summaries Section
        dbc.Row([
            dbc.Col(dbc.Card([ 
                dbc.CardHeader("🔥 Max Fires Count"), 
                dbc.CardBody(html.H4(id='max-fires', style={'color': '#fff','fontWeight': 'bold'})) 
            ], color='#ff9750', inverse=True)),
            dbc.Col(dbc.Card([ 
                dbc.CardHeader("📍 Total Area Burned (ha)"), 
                dbc.CardBody(html.H4(id='total-area', style={'color': '#fff', 'fontWeight': 'bold'})) 
            ], color='#f97d16', inverse=True)),
            dbc.Col(dbc.Card([ 
                dbc.CardHeader("📊 Average Area Burned (ha)"), 
                dbc.CardBody(html.H4(id='avg-area', style={'color': '#fff', 'fontWeight': 'bold'})) 
            ], color='#ec5300', inverse=True)),
        ], style={'margin': '20px'}),

        # # Colorful and Beautiful Bar Chart
        # dcc.Graph(id='bar-chart', style={'height': '500px'}),
        # Bar Chart Section in Home Layout
        dcc.Graph(
        id='bar-chart',
        style={
            'height': '500px',
            'padding': '20px',  # Add padding to ensure content stays within boundaries
            'paddingLeft': '30px',
            'margin': '0 auto',  # Center the graph horizontally if necessary
            'opacity': '0.8',
            'boxSizing': 'border-box'  # Ensure padding doesn't affect dimensions
            # 'backgroundColor': '#1e1e1e',  # Optional background color for clarity
            # 'borderRadius': '8px'  # Rounded corners for aesthetics
            # 'borderRadius': '8px'  # Rounded corners for aesthetics
            }
        ),

        # Embed HTML file below the bar chart (same height as bar chart)
        
        # Other graphs if needed
        # dcc.Graph(id='choropleth-map', style={'height': '400px'}),
        # dcc.Graph(id='overview-graph', style={'height': '400px'})
    ], style={
        'position': 'relative',  # Ensure the content sits on top of the background
        'overflow': 'auto',
        'boxSizing': 'border-box',
        'zIndex': '2',  # Ensure the content is above the background
        'backgroundImage': 'url(/assets/wildfire.webp)',  # Background image URL
        'backgroundSize': 'cover',  # Make the image cover the entire background
        'backgroundPosition': 'center',  # Center the image
        'backgroundRepeat': 'no-repeat',  # Prevent repeating of the image
        'height': '100vh',  # Ensure the background image covers the entire viewport height
        'paddingLeft': '265px',  # Ensure the background starts after the sidebar
        'paddingTop': '10px',  # Optional: add some top padding for spacing
        'paddingRight': '20px'  # Optional: add some right padding for spacing
    })
], style={
    'position': 'relative',  # Ensure the content sits on top of the background
    'minHeight': '100vh',  # Full height of the viewport
    'zIndex': '0',  # Ensure the background image stays behind the content
    'width': '100vw',
    'height': '100vh',
    'overflow': 'hidden',  # Prevent global overflow
    'margin': '0',
    'padding': '0',
    'boxSizing': 'border-box'
})


@app.callback(
    [Output('max-fires', 'children'),
     Output('total-area', 'children'),
     Output('avg-area', 'children')],
    [Input('year-dropdown', 'value'),
     Input('commune-dropdown', 'value')]  # Adding the commune dropdown as input
)
def update_data_summaries(selected_year, selected_commune):
    # Filter the dataframe by the selected year and commune
    filtered_df = df
    if selected_year:
        filtered_df = filtered_df[filtered_df['Alerte'].dt.year == selected_year]
    if selected_commune:
        filtered_df = filtered_df[filtered_df['Commune'] == selected_commune]
    
    # Calculate the required statistics
    max_fires = filtered_df['Code INSEE'].nunique()  # Example of unique fire events
    total_area = filtered_df['Surface parcourue (m2)'].sum() / 10000  # Convert to hectares
    avg_area = filtered_df['Surface parcourue (m2)'].mean() / 10000  # Convert to hectares

    return max_fires, total_area, avg_area


@app.callback(
    Output('bar-chart', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('commune-dropdown', 'value')]  # Add commune dropdown as input
)
def update_bar_chart(selected_year, selected_commune):
    # Filter the dataframe by the selected year and commune
    filtered_df = df
    if selected_year:
        filtered_df = filtered_df[filtered_df['Alerte'].dt.year == selected_year]
    if selected_commune:
        filtered_df = filtered_df[filtered_df['Commune'] == selected_commune]
    
    # Group by commune and calculate the total area burned
    area_by_commune = filtered_df.groupby('Commune')['Surface parcourue (m2)'].sum() / 10000  # Convert to hectares
    
    # Create the bar chart
    fig = px.bar(area_by_commune,
                 x=area_by_commune.index,
                 y=area_by_commune.values,
                 labels={'x': 'Commune', 'y': 'Total Area Burned (ha)'},
                 title=f"Total Area Burned (ha) by Commune in {selected_year}" if selected_year else "Total Area Burned (ha) by Commune",
                 color=area_by_commune.values,  # Color based on the area burned
                 color_continuous_scale='Viridis'  # Use a color scale for better aesthetics
                )
    
    fig.update_layout(
        template='plotly_dark',
        xaxis_tickangle=-45,
        xaxis={'title': 'Commune', 'tickmode': 'array'},
        yaxis={'title': 'Total Area Burned (ha)'},
        margin={'t': 50, 'b': 50, 'l': 50, 'r': 50},
        # plot_bgcolor='#1e1e1e',  # Background matches container
        # paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for alignment
        autosize=True  # Automatically adjust to fit the container
    )
    
    return fig


# --- Insights Layout ---
insights_layout = html.Div([
    sidebar,  # Sidebar with dropdowns (year and commune)

    # Title with solid background
    html.Div(
        style={
        'backgroundColor': '#bd4343',  # Solid background color
        'width': '100%',
        'position': 'relative',
        'zIndex': '2',  # Makes sure it's on top
        'boxShadow': '0px 0px 0px rgba(0, 0, 0, 0)',
        # 'paddingLeft': '265px',  # Adjust for sidebar width
        'overflow': 'hidden',  # Prevents any content overflow
        'boxSizing': 'border-box'
    }),

    # Insights Content with the same background image and no overflow
    html.Div([
        dbc.Row([
            # Left side - Pie Chart and Bubble Chart
            dbc.Col([
                dcc.Graph(
                    id='pie-chart',
                    style={
                        'height': '330px',
                        'marginBottom': '20px',
                        'backgroundColor': '#000',  # Black background for Plotly graphs
                        'borderRadius': '10px',  # Rounded corners for aesthetic appeal
                        'opacity': '0.8'
                    }
                ),
                dcc.Graph(
                    id='bubble-chart',
                    style={
                        'height': '330px',
                        'backgroundColor': '#000',  # Black background for Plotly graphs
                        'borderRadius': '10px',  # Rounded corners for aesthetic appeal
                        'opacity': '0.8'
                    }
                )
            ], width=5),

            # Right side - Choropleth Map with more space
            dbc.Col([
                dcc.Graph(
                    id='choropleth-map',
                    style={
                        'height': '680px',  # Increased height for the map
                        'width': '680px',
                        'backgroundColor': '#000',  # Black background for Plotly graphs
                        'borderRadius': '0px',  # Rounded corners for aesthetic appeal
                        'opacity': '0.8'
                    }
                )
            ], width=7)
        ], style={'marginLeft': '20px', 'padding': '20px'})
    ], style={
        'paddingTop': '10px',
        'backgroundImage': 'url(/assets/wildfire.webp)',  # Background image for Insights page
        'backgroundSize': 'cover',  # Ensure it covers the entire background
        'backgroundPosition': 'center',
        'backgroundRepeat': 'no-repeat',  # Prevent repeating of the image
        'height': '100vh',  # Full height of the viewport
        'paddingLeft': '265px',  # Ensure the background starts after the sidebar
        'paddingTop': '10px',  # Optional: add some top padding for spacing
        'paddingRight': '20px',  # Optional: add some right padding for spacing
        'overflow': 'hidden',  # Ensure there is no overflow (scrolling)
        'boxSizing': 'border-box'  # Ensure padding doesn't affect the layout
    })
], style={
    'position': 'relative',
    'minHeight': '100vh',  # Full height of the viewport
    'zIndex': '0',  # Ensure the background image stays behind the content
    'width': '100vw',
    'height': '100vh',
    'overflow': 'hidden',  # Prevent global overflow
    'margin': '0',
    'padding': '0',
    'boxSizing': 'border-box'
})



# --- Callbacks to update graphs dynamically ---
@app.callback(
    [Output('pie-chart', 'figure'),
     Output('bubble-chart', 'figure'),
     Output('choropleth-map', 'figure')],
    [Input('year-dropdown', 'value'),
     Input('commune-dropdown', 'value')]
)
def update_insights(selected_year, selected_commune):
    # Filter the data based on selected year and commune
    filtered_df = df[df['Alerte'].dt.year == selected_year] if selected_year else df
    filtered_df = filtered_df[filtered_df['Commune'] == selected_commune] if selected_commune else filtered_df
    
    # --- Pie Chart: Fire origin distribution ---
    fire_origin_distribution = filtered_df['Origine de l\'alerte'].value_counts().reset_index()
    fire_origin_distribution.columns = ['Origin', 'Count']
    pie_fig = px.pie(fire_origin_distribution, names='Origin', values='Count', title="Fire Origin Distribution", hole=0.5)
    # Apply the Plotly dark theme and layout adjustments
    pie_fig.update_layout(
    template='plotly_dark',  # Dark theme for the entire chart
    margin={'t': 50, 'b': 50, 'l': 0, 'r': 50},  # Adjust margins for clarity
    autosize=True  # Automatically adjust the chart to fit the container
    )
    
    # --- Bubble Chart: Fire occurrences by DFCI code ---
    dfci_fire_distribution = filtered_df['Code du carreau DFCI'].value_counts().reset_index()
    dfci_fire_distribution.columns = ['DFCI_Code', 'Fire_Count']
    dfci_fire_distribution['Impact'] = dfci_fire_distribution['Fire_Count'] * 10
    bubble_fig = px.scatter(dfci_fire_distribution, x='DFCI_Code', 
                            y='Fire_Count', 
                            size='Impact', color='Fire_Count', 
                            title="Fire Occurrences by DFCI Code", size_max=20)
    # Apply the Plotly dark theme and layout adjustments
    bubble_fig.update_layout(
    template='plotly_dark',  # Dark theme for the entire chart
    margin={'t': 50, 'b': 50, 'l': 0, 'r': 50},  # Adjust margins for clarity
    autosize=True  # Automatically adjust the chart to fit the container
    )
    # # 🌍 **Choropleth Map: Filtered by Commune**
    # filtered_gdf = merged.copy()
    # map_center = {"lat": 43.5, "lon": 5.4}  # Default center for initial state
    # projection_scale = 12  # Default zoom level

    # # Commune Selection and Dynamic Centering
    # if selected_commune:
    #     filtered_gdf = filtered_gdf[filtered_gdf['Commune'] == selected_commune]
    
    # if not filtered_gdf.empty:
    #     # Calculate the centroid of the selected commune for zooming
    #     commune_center = filtered_gdf.geometry.centroid.iloc[0]
    #     map_center = {"lat": commune_center.y, "lon": commune_center.x}
    #     projection_scale = 10  # Zoom closer to the selected commune
    # else:
    #     print("⚠️ Selected commune not found in the dataset!")

    # # Ensure valid geometries
    # filtered_gdf = filtered_gdf[filtered_gdf.geometry.notnull()]
    # filtered_gdf = filtered_gdf[filtered_gdf.is_valid]

    # # Plot Choropleth Map
    # choropleth_fig = px.choropleth(
    # filtered_gdf,
    # template='plotly_dark',
    # geojson=filtered_gdf.geometry.__geo_interface__,
    # locations=filtered_gdf.index,
    # color='POPULATION',  # Adjust as needed
    # hover_name='Commune',
    # hover_data=['SUPERFICIE', 'Surface parcourue (m2)'],
    # color_continuous_scale='Viridis',
    # title="Bouches-du-Rhône Communes & Population"
    # )

    # # Update map properties for zoom and centering
    # choropleth_fig.update_geos(
    # fitbounds="locations" if selected_commune else False,  # Fit to selected commune
    # visible=False,
    # showcoastlines=False,
    # projection_type="mercator",
    # center=map_center,
    # projection_scale=projection_scale
    # )

    # # Adjust layout for full visibility
    # choropleth_fig.update_layout(
    # autosize=True,
    # height=680,
    # margin={"t": 50, "b": 20, "l": 20, "r": 20}
    # )
    

    



    # return pie_fig, bubble_fig, choropleth_fig


    # Create the choropleth map
    # # Create the choropleth map using Plotly
    # choropleth_fig = px.choropleth(
    # merged_gdf,
    # template='plotly_dark',
    # geojson=merged_gdf.geometry.__geo_interface__,  # Use the geometry column for geojson
    # locations=merged_gdf.index,  # Use index to refer to locations
    # color='POPULATION',  # Replace this with the column you want to visualize (e.g., fire occurrences)
    # hover_name='NOM_COM',  # Commune names
    # hover_data=['SUPERFICIE', 'Surface parcourue (m2)'],  # Add columns from df you want to display on hover
    # color_continuous_scale='Viridis',  # You can change the color scale if needed
    # title="Bouches-du-Rhône Communes & Population"
    # )

    # # Customize the map's appearance to remove all background land, coastlines, etc. 
    # choropleth_fig.update_geos(
    # fitbounds="locations",  # Fit map bounds to locations
    # visible=False,  # Hide axis
    # showcoastlines=False,  # Hide coastlines
    # coastlinecolor="white",  # No coastline color
    # projection_type="mercator",  # Projection type for better global visualization
    # center={"lat": 43.5, "lon": 5.4},  # Adjust the center to focus on the area you want (e.g., Bouches-du-Rhône)
    # projection_scale=3,  # Adjust scale to zoom in
    # showland=False,  # Remove land background
    # showsubunits=False,  # Hide borders or subunits
    # showcountries=False  # Hide countries' background
    # )

    # # Customize the figure layout for better control over size and appearance
    # choropleth_fig.update_layout(
    # autosize=True,  # Automatically adjust the chart to fit the container
    # margin={"t": 50, "b": 20, "l": 20, "r": 20},  # Adjust margins to allow more map space
    # geo=dict(
    #     projection=dict(type="mercator"),  # Ensure Mercator projection is used
    #     showland=False,  # No land background
    #     showcoastlines=False,  # No coastlines
    #     showcountries=False,  # No countries
    #     showsubunits=False,  # No subunits (borders between regions)
    #     landcolor="rgba(0,0,0,0)",  # Make land background fully transparent
    #     subunitcolor="rgba(0,0,0,0)",  # Make subunit borders transparent
    # )
    # )
    
    # return pie_fig, bubble_fig, choropleth_fig

    # # 🌍 **Choropleth Map: Filtered by Commune**
    # filtered_gdf = merged.copy()
    # if selected_commune:
    #     filtered_gdf = filtered_gdf[filtered_gdf['Commune'] == selected_commune]
    
    # choropleth_fig = px.choropleth(
    #     filtered_gdf,
    #     template='plotly_dark',
    #     geojson=filtered_gdf.geometry.__geo_interface__,  # Use the geometry column
    #     locations=filtered_gdf.index,
    #     color='POPULATION',  # Example column, replace as needed
    #     hover_name='Commune',
    #     hover_data=['SUPERFICIE', 'Surface parcourue (m2)'],
    #     color_continuous_scale='Viridis',
    #     title="Bouches-du-Rhône Communes & Population"
    # )
    
    # # Adjust map visualization
    # choropleth_fig.update_geos(
    #     fitbounds="locations",
    #     visible=False,
    #     showcoastlines=False,
    #     projection_type="mercator",
    #     center={"lat": 43.5, "lon": 5.4},
    #     projection_scale=3
    # )
    
    # choropleth_fig.update_layout(
    #     autosize=True,
    #     margin={"t": 50, "b": 20, "l": 20, "r": 20}
    # )
    
    import numpy as np

# 🌍 **Choropleth Map: Filtered by Commune**
    filtered_gdf = merged.copy()

# Apply the commune filter if selected
    if selected_commune:
        filtered_gdf = filtered_gdf[filtered_gdf['Commune'] == selected_commune]

# Calculate Population Intensity (Population Density: population/area)
    filtered_gdf['Population Intensity'] = filtered_gdf['POPULATION'] / filtered_gdf['SUPERFICIE']

# Apply logarithmic transformation to the Population Intensity for better visualization
    filtered_gdf['Density'] = np.log1p(filtered_gdf['Population Intensity'])

# Create the choropleth map with logarithmic scaling for better visual differentiation
    choropleth_fig = px.choropleth(
    filtered_gdf,
    template='plotly_dark',
    geojson=filtered_gdf.geometry.__geo_interface__,  # Use the geometry column
    locations=filtered_gdf.index,
    color='Density',  # Use the log-transformed Population Intensity
    hover_name='Commune',
    hover_data=['SUPERFICIE', 'Surface parcourue (m2)', 'POPULATION', 'Population Intensity'],
    color_continuous_scale='Viridis',  # Adjust color scale as per intensity
    range_color=[filtered_gdf['Density'].min(), filtered_gdf['Density'].max()],  # Adjust color scale range
    title="Bouches-du-Rhône Communes & Population Intensity"
    )

# Adjust map visualization settings
    choropleth_fig.update_geos(
    fitbounds="locations",
    visible=False,
    showcoastlines=False,
    projection_type="mercator",
    center={"lat": 43.5, "lon": 5.4},
    projection_scale=3
    )

# Update layout and adjust margins
    choropleth_fig.update_layout(
    autosize=True,
    margin={"t": 50, "b": 20, "l": 20, "r": 20}
    )

# Return the updated figures (including the choropleth map)
# return pie_fig, bubble_fig, choropleth_fig


    # Return the updated figures (including the choropleth map)
    return pie_fig, bubble_fig, choropleth_fig



# --- Trends Layout ---
# --- Trends Layout --- 
trends_layout = html.Div([
    sidebar,  # Sidebar for filters like 'year'

    html.Div([
        # Top Section: Yearly and Monthly Graphs Side by Side
        html.Div([
            # Yearly Trends Chart (Left Side, Fully Extended Vertically)
            html.Div([
                dcc.Graph(id='yearly-trends-graph')
            ], style={
                'flex': '0.3',  # 30% width
                'height': '100vh',  # Full vertical height
                'overflow': 'hidden',
                'opacity':'0.8',
                'paddingRight':'13px'
            }),

            # Monthly Trends Chart (Right Side, Full Height)
            html.Div([
                dcc.Graph(id='monthly-trends-graph')
            ], style={
                'flex': '0.7',  # 70% width
                'height': '100vh',
                'overflow': 'hidden',
                'opacity':'0.8'
            })
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'height': '80vh',  # Top section takes 80% of the viewport height
            'overflow': 'hidden',
            'opacity':'0.8'
        }),

        # Bottom Section: Hourly Graph (Full Width Below Both Graphs)
        html.Div([
            dcc.Graph(id='hourly-trends-graph')
        ], style={
            'width': '100%',  # Full width of the page
            # 'height': '44vh',  # Takes 20% of the viewport height
            'height': 'calc(40vh)',
            'paddingTop': '0px',
            'paddingBottom': '20px',  # Space below the graph
            # 'overflow': 'hidden'
            'overflowY': 'auto',
            'opacity':'0.8'
        })

    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'height': '100vh',
        'padding': '20px',
        'overflow': 'hidden'
    })
], style={
    'backgroundImage': 'url(/assets/wildfire.webp)',  # Background image
    'backgroundSize': 'cover',
    'backgroundPosition': 'center',
    'backgroundRepeat': 'no-repeat',
    'height': '100vh',
    'paddingLeft': '265px',
    'overflow': 'hidden',
    'boxSizing': 'border-box'
})



@app.callback(
    [
        Output('monthly-trends-graph', 'figure'),
        Output('hourly-trends-graph', 'figure'),
        Output('yearly-trends-graph', 'figure')
    ],
    [
        Input('year-dropdown', 'value')
    ]
)
def update_trends(selected_year):
    # Filter data by selected year
    filtered_df = df.copy()
    if selected_year:
        filtered_df = filtered_df[filtered_df['Alerte'].dt.year == selected_year]

    
    # Group by Month
    monthly_trend = filtered_df.groupby(filtered_df['Alerte'].dt.to_period('M')).size().reset_index(name='Fire Count')
    monthly_trend['Alerte'] = monthly_trend['Alerte'].dt.strftime('%Y-%m')
    
    # Group by Hour
    hourly_trend = filtered_df.groupby(filtered_df['Alerte'].dt.hour).size().reset_index(name='Fire Count')
    hourly_trend['Hour'] = hourly_trend['Alerte']  # Rename for clarity
    
    # Group by Year
    yearly_trend = filtered_df.groupby(filtered_df['Alerte'].dt.year).size().reset_index(name='Fire Count')
    
    # --- Monthly Trend Plot ---
    monthly_fig = px.line(
        monthly_trend,
        x='Alerte',
        y='Fire Count',
        title='Monthly Fire Alerts'
    )
    monthly_fig.update_layout(
        template='plotly_dark',
        xaxis_title='Month',
        yaxis_title='Fire Count',
        margin={'t': 50, 'b': 50, 'l': 50, 'r': 50},
        showlegend=False  # Explicitly disable legend
    )
    
    # --- Hourly Trend Plot ---
    hourly_fig = px.bar(
        hourly_trend,
        x='Hour',
        y='Fire Count',
        title='Hourly Fire Alerts',
        color='Fire Count',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )

    hourly_fig.update_layout(
        template='plotly_dark',
        xaxis_title='Hour of the Day',
        yaxis_title='Number of Fire Alerts',
        margin={'t': 40, 'b': 40, 'l': 40, 'r': 40},  # Compact margins
        height=210,  # Reduce the graph plot height inside the box
        font=dict(size=10),  # Reduce font size for better fit
        bargap=0.1,  # Slightly reduce gap between bars
        coloraxis_showscale=False,  # Hide the color scale legend
        showlegend=False  # Hide legend
    )

    # Optimize axis ticks and labels
    hourly_fig.update_xaxes(tickangle=0, tickfont=dict(size=8), automargin=True)
    hourly_fig.update_yaxes(tickfont=dict(size=8), automargin=True)

    # Adjust bar size to avoid clutter
    hourly_fig.update_traces(marker=dict(line=dict(width=0.5)))

    # hourly_fig.update_traces(showlegend=False)

    
    # --- Yearly Trend Plot ---
    yearly_fig = px.bar(
        yearly_trend,
        x='Fire Count',
        y='Alerte',
        orientation='h',
        title='Yearly Fire Alerts',
        color='Fire Count',
        color_continuous_scale='Cividis'
    )

    # **Filter Y-axis labels to display only the selected year**
    if selected_year:
        yearly_fig.update_yaxes(
            tickvals=[selected_year],
            ticktext=[str(selected_year)]
        ) 

    yearly_fig.update_layout(
        template='plotly_dark',
        xaxis_title='Fire Count',
        yaxis_title='Year',
        margin={'t': 50, 'b': 50, 'l': 50, 'r': 50},
        coloraxis_showscale=False  # Disable the color scale legend
    )
    yearly_fig.update_traces(showlegend=False)
    
    return monthly_fig, hourly_fig, yearly_fig


# --- QGIS Layout ---
# --- QGIS Mapping Layout (Fourth Page) ---
# QGIS Mapping Page Layout
qgis_mapping_layout = html.Div([
    sidebar,  # Sidebar for filters like 'year'

    # # Title for the fourth page
    # html.Div([
    #     html.H1("QGIS Mapping", style={  # Title for the page
    #         'textAlign': 'left',  # Title aligned to the left
    #         'color': '#002855',  # Title color
    #         'fontSize': '26px',  # Font size of the title
    #         'fontWeight': 'bold',  # Bold title
    #         'padding': '10px',
    #         'margin': '0',  # Remove default margin
    #         'boxSizing': 'border-box'
    #     }),
    # ], style={  # Styling the title container
    #     'backgroundColor': '#bd4343',  # Title background color
    #     'width': '100%',
    #     'position': 'relative',  # Ensures the title is above other sections
    #     'zIndex': '2',  # Makes sure the title is on top
    #     'paddingLeft': '265px',  # Offset by sidebar width
    #     'overflow': 'hidden',  # Prevents content overflow
    #     'boxSizing': 'border-box'
    # }),

    # Embed HTML file (QGIS map) below the title
    html.Div([  # Embed iframe for the HTML file
        html.Iframe(
            src='/html/index.html',  # Link to your HTML file (adjusted Flask route)
            width="100%",  # Set to full width (adjust based on the sidebar width)
            height="100%",  # Make iframe take 100% height of the container
            style={
                'border': 'none',  # No border around the iframe
                'boxSizing': 'border-box',  # Ensure proper box sizing
                'borderRadius': '0px',  # Optional: Rounded corners for aesthetics
                'position': 'absolute',  # Absolute positioning to place it correctly
                'top': '0px',  # Title bar height (80px) pushed down the iframe
                'left': '0',  # Align iframe to the left side
                'right': '0',  # Stretch it to the right edge of the screen
                'bottom': '0',  # Ensure it fills vertically as well
            }
        )
    ], style={  # Style the iframe container
        'height': 'calc(100vh - 0px)',  # Full height minus title height (80px)
        'width': 'calc(100vw - 265px)',  # Full width minus sidebar width (265px)
        'padding': '0',  # No padding
        'backgroundColor': 'transparent',  # Transparent background
        'margin': '0',  # No margin around the container
        'boxSizing': 'border-box',  # Prevent overflow and adjust box model
        'position': 'absolute',  # Absolute positioning for better control
        'bottom': '0',  # Remove bottom margin to ensure full height
        'left': '265px',  # Start after the sidebar width (265px)
    })

], style={  # Main container style for the entire page
    'position': 'relative',  # Ensures proper layout placement
    'width': '100vw',  # Full width of the viewport
    'height': '100vh',  # Full height of the viewport
    'boxSizing': 'border-box',
    'overflow': 'hidden',  # Prevent overflow
    'margin': '0',  # Remove margins from the body
    'padding': '0',  # No padding around the entire page
})







# --- Callbacks ---
@app.callback(
    [Output('hidden-sidebar', 'style'),
     Output('toggle-sidebar', 'children'),
     Output('toggle-sidebar', 'style')],
    [Input('toggle-sidebar', 'n_clicks')],
    [State('hidden-sidebar', 'style'),
     State('url', 'pathname')]  # Add pathname to check current page
)
def toggle_sidebar(toggle_clicks, current_style, pathname):
    if pathname == '/':  # Only show the hidden sidebar on the home page
        if current_style['display'] == 'none':
            current_style['display'] = 'block'
            icon = "◀️"  # Sidebar(02)
            btn_style = {'left': '540px'}
        else:
            current_style['display'] = 'none'
            icon = "▶️"  # Sidebar(01)
            btn_style = {'left': '245px'}
    else:
        current_style['display'] = 'none'  # Hide sidebar on other pages
        icon = "▶️"  # Sidebar(01)
        btn_style = {'left': '245px'}
    
    return current_style, icon, {**toggle_button.style, **btn_style}

# --- Routing ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return home_layout
    elif pathname == '/insights':
        return insights_layout
    elif pathname == '/trends':
        return trends_layout
    
    elif pathname == '/qgis_mapping':  # Ensure that this matches the link you are using
        return qgis_mapping_layout
 
    return html.Div("Page not found")

if __name__ == '__main__':
    app.run_server(debug=True)

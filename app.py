import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import geopandas as gpd
import dash_bootstrap_components as dbc
import unidecode
import plotly.graph_objects as go
from flask import send_from_directory

# -------------------------------
# Load Data & Cleaning
# -------------------------------
# --- 1. Load CSV Data ---
try:
    df1 = pd.read_csv('Classeur1.csv', encoding='ISO-8859-1', delimiter=';', on_bad_lines='skip')
except UnicodeDecodeError:
    df1 = pd.read_csv('Classeur1.csv', encoding='latin1', delimiter=';', on_bad_lines='skip')

# Extract the first two digits of 'Code INSEE' from df1 and filter for the Department '13'
df = df1[df1['Code INSEE'].str[:2] == '13']
 
# Clean column names and types
df.columns = df.columns.str.strip()
df['Alerte'] = pd.to_datetime(df['Alerte'], errors='coerce')
df['Code INSEE'] = df['Code INSEE'].astype(str).str.strip()

# Filter CSV by year range (1973–2024) - Here all years took for the entire df
df = df[(df['Alerte'].dt.year >= 1970) & (df['Alerte'].dt.year <= 2024)]

# Drop rows with NaN values in any column
df = df.dropna(how='any')

# Drop columns that contain all NaN values
df = df.dropna(axis=1, how='all')  

# --- 2. Load Shapefile ---

#shapefile_path = "C:/Users/Lutfi/Desktop/Forest Fire Project/Dashboard_Project/shapefile/Commune_BR_13.shp"
shapefile_path = "shapefile/Commune_BR_13.shp"
gdf = gpd.read_file(shapefile_path)
gdf.columns = gdf.columns.str.strip()
gdf['INSEE_COM'] = gdf['INSEE_COM'].astype(str).str.strip()
gdf['NOM_DEPT'] = gdf['NOM_DEPT'].astype(str).str.strip()

# Check for NaN or missing values
missing_commune_gdf = gdf[gdf['INSEE_COM'].isnull() | (gdf['INSEE_COM'] == '')]
# print(missing_commune_gdf)

# Ensure Code INSEE exists and clean it
if 'Code INSEE' not in df.columns:
    raise ValueError("'Code INSEE' column not found in CSV file.")

df['Code INSEE'] = df['Code INSEE'].astype(str).str.strip()

# Check common keys
common_insee = set(gdf['INSEE_COM']) & set(df['Code INSEE'])
# print(f"Number of common INSEE codes: {len(common_insee)}")

if len(common_insee) == 0:
    raise ValueError("No common INSEE codes found between shapefile and CSV!")

# -------------------------------
# Merge Shapefile and CSV
# -------------------------------
merged = gdf.merge(df, how='left', left_on='INSEE_COM', right_on='Code INSEE')

# Drop rows with null geometries or missing values in important fields
# merged = merged.dropna(subset=['surf_ha', 'geometry'])

# Ensure 'surf_ha' is numeric
# merged['surf_ha'] = pd.to_numeric(merged['surf_ha'], errors='coerce')
# merged = merged.dropna(subset=['surf_ha'])

# print(f"Merged GeoDataFrame has {len(merged)} rows after dropping null geometries and values.")

# -------------------------------
# Validate Geometries
# -------------------------------
invalid_geometries = merged[~merged.is_valid]
if not invalid_geometries.empty:
    print(f"Found {len(invalid_geometries)} invalid geometries. These will be ignored.")
merged = merged[merged.is_valid]

# Ensure no empty geometries
merged = merged[~merged.geometry.is_empty]

if merged.empty:
    raise ValueError("Merged GeoDataFrame is empty after filtering valid geometries!")

# -------------------------------
# Set CRS and Reproject gdf
# -------------------------------
if merged.crs is None:
    merged = merged.set_crs(epsg=2154)  # Assuming original CRS
merged = merged.to_crs(epsg=4326)

# print("CRS reprojected to EPSG:4326.")

# -------------------------------
# Export to GeoJSON
# -------------------------------
geojson_file_path = "C:/Users/Lutfi/Desktop/Forest Fire Project/Dashboard_Project/geojson/all_communes.geojson"
merged.to_file(geojson_file_path, driver='GeoJSON')

# print(f"GeoJSON successfully created at {geojson_file_path}")
# print(f"Number of features in GeoJSON: {len(merged)}")

# -------------------------------
# Final Validation Output
# -------------------------------
# Filter the GeoDataFrame by CODE_DEPT == 13 (Bouches-du-Rhône)
# merged = merged[merged['CODE_DEPT'] == 13]

# print(merged[['INSEE_COM', 'Code INSEE', 'surf_ha']].head())

# Fill missing 'Code INSEE' values with values from 'INSEE_COM'
merged['Code INSEE'] = merged['Code INSEE'].fillna(merged['INSEE_COM'])

# Replace empty strings in 'Code INSEE' with values from 'INSEE_COM'
merged.loc[merged['Code INSEE'] == '', 'Code INSEE'] = merged['INSEE_COM']

# Check if 'Code INSEE' contains NaN or empty values after the replacement
merged_miss = merged[merged['Code INSEE'].isnull() | (merged['Code INSEE'] == '')]
# print(merged_miss)


# -------------------------------
# QGIS html file directory
# -------------------------------
# Set the path to the directory containing the HTML file
# html_file_directory = r'C:\Users\Lutfi\Desktop\Forest Fire Project\Dashboard_Project\qgis2web_2024_11_06-12_39_04_012529'
html_file_directory = r'qgis2web_2024_11_06-12_39_04_012529'


# ----------------------------------------
# ✅✅✅ Dash App Initialization ✅✅✅
# ----------------------------------------
app = dash.Dash(__name__, external_stylesheets=['/assets/styles.css'], suppress_callback_exceptions=True)
# app.title = "Forest Fire Analytical Dashboard"
server = app.server

@app.server.route('/html/<path:path>')
def serve_html(path):
    return send_from_directory(html_file_directory, path)


# --------------------------------
#  Dash App Sidebar
# ---------------------------------
# --- Sidebar Components ---
sidebar = html.Div([
    html.H1("Forest Fire Analytical Dashboard", className='sidebar-title'),
    html.Label("Select Year", className='sidebar-label'),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': str(year), 'value': year} for year in df['Alerte'].dt.year.dropna().unique()],
        placeholder="Select a Year",
        className='dropdown'
    ),
    html.Label("Select Commune", className='sidebar-label'),
    dcc.Dropdown(
        id='commune-dropdown',
        options=[{'label': commune, 'value': commune} for commune in df['Commune'].unique()],
        placeholder="Select a Commune",
        className='dropdown'
    ),
    html.Hr(className='sidebar-divider'),
    dbc.Nav([
        dbc.NavLink("🏠 Home", href='/', active='exact', className='nav-link'),
        dbc.NavLink("📊 Insights", href='/insights', active='exact', className='nav-link'),
        dbc.NavLink("📈 Temporal Trends", href='/trends', active='exact', className='nav-link'),
        # dbc.NavLink("🗺️ QGIS Mapping", href='/QGIS Mapping', active='exact', className='nav-link'),

        dbc.NavLink("🗺️ QGIS Mapping", href='/qgis_mapping', active='exact', className='nav-link')

    ], vertical=True, pills=True, className='sidebar-nav'),
    html.Div([
        html.Img(src="/assets/LOGO_AMU.png", className='sidebar-logo'),
        html.P("Data Source: Défense de la Forêt Contre les Incendies", className='sidebar-footer-text')
    ], className='sidebar-footer')
], id='main-sidebar')

# --- Toggle Button ---
toggle_button = html.Button(
    "▶️",
    id='toggle-sidebar',
    className='toggle-button'
)

# --- Hidden Sidebar ---
hidden_sidebar = html.Div([
    html.H3("🔑 Key Information", className='hidden-sidebar-title'),
    html.P("This dashboard visualizes forest fire data in the Bouches-du-Rhône region from 2018 to 2024."),
    html.P("Key insights include total fires, affected area, and time-based trends."),
    html.P("This dashboard is part of the final project for the Geovisualization course held at the University of Aix-Marseille."),
    html.P("The project aims to showcase the use of data visualization techniques in analyzing and understanding forest fire activity."),
    html.P("Use the navigation menu to switch between views and explore the data in detail."),
], id='hidden-sidebar', style={'display': 'none'})


# --------------------------------
#  Dash App Layouts
# ---------------------------------
# 1. --- Home Layout ---
home_layout = html.Div([
    sidebar,
    html.Div([ 
        html.Div( 
            html.H1("Bouches-du-Rhône Department of France", className='title-text'),
            className='title-container'
        ),
        html.Div([  
            dbc.Row([  
                dbc.Col(dbc.Card([
                    dbc.CardHeader("🔥 Max Fires Count"),
                    dbc.CardBody(html.H4(id='max-fires'))
                ], className='card max-fires')),
                dbc.Col(dbc.Card([
                    dbc.CardHeader("📍 Total Area Burned (ha)"),
                    dbc.CardBody(html.H4(id='total-area'))
                ], className='card total-area')),
                dbc.Col(dbc.Card([
                    dbc.CardHeader("📊 Avg Area Burned (ha)"),
                    dbc.CardBody(html.H4(id='avg-area'))
                ], className='card avg-area')),
                dbc.Col(dbc.Card([
                    dbc.CardHeader("⬆️ Max Burned Area(ha)"),
                    dbc.CardBody(html.H4(id='max-area'))
                ], className='card max-area')),
                dbc.Col(dbc.Card([
                    dbc.CardHeader("⬇️ Min Burned Area(ha)"),
                    dbc.CardBody(html.H4(id='min-area'))
                ], className='card min-area'))
            ])
        ], className='summary-section'),
        dcc.Graph(id='bar-chart', className='bar-chart')
    ], className='main-content'),
], className='home-layout')


# --- Callbacks for updating data summaries and bar chart ---
@app.callback(
    [Output('max-fires', 'children'),
     Output('total-area', 'children'),
     Output('avg-area', 'children'),
     Output('max-area', 'children'),
     Output('min-area', 'children')],
     
    [Input('year-dropdown', 'value'),
     Input('commune-dropdown', 'value')]
)
def update_data_summaries(selected_year, selected_commune):
    filtered_df = df
    if selected_year:
        filtered_df = filtered_df[filtered_df['Alerte'].dt.year == selected_year]
    if selected_commune:
        filtered_df = filtered_df[filtered_df['Commune'] == selected_commune]

    max_fires = filtered_df['Alerte'].nunique()
    total_area = filtered_df['Surface parcourue (m2)'].sum() / 10000
    avg_area = filtered_df['Surface parcourue (m2)'].mean() / 10000
    # Format the values to 2 decimal places
    total_area = round(total_area, 2)
    avg_area = round(avg_area, 2)
    max_area = filtered_df['Surface parcourue (m2)'].max()
    min_area = filtered_df['Surface parcourue (m2)'].min()

    return max_fires, total_area, avg_area, max_area, min_area


@app.callback(
    Output('bar-chart', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('commune-dropdown', 'value')]
)
def update_bar_chart(selected_year, selected_commune):
    filtered_df = df
    if selected_year:
        filtered_df = filtered_df[filtered_df['Alerte'].dt.year == selected_year]
    if selected_commune:
        filtered_df = filtered_df[filtered_df['Commune'] == selected_commune]

    area_by_commune = filtered_df.groupby('Commune')['Surface parcourue (m2)'].sum() / 10000
    fig = px.bar(area_by_commune, 
             x=area_by_commune.index,
             y=area_by_commune.values,
             color=area_by_commune.values,  
             color_continuous_scale='Viridis',
             title='Total Area Burned by Commune')
    
    # --- Update layout for the chart ---
    fig.update_layout(
    template='plotly_dark', 
    xaxis_tickangle=-45, 
    xaxis={'title': 'Commune', 'tickmode': 'array'},  
    yaxis={'title': 'Total Area Burned (ha)'},  
    # margin={'t': 50, 'b': 50, 'l': 50, 'r': 50},  
    autosize=True,  
    plot_bgcolor='rgba(0,0,0,0)',  
    paper_bgcolor='rgba(0,0,0,0)',
    )

    # Now using chart in dcc.Graph component
    # dcc.Graph(id='bar-chart', figure=fig, className='bar-chart')  # Matches CSS)
    return fig


# 2. --- Insights Layout ---
insights_layout = html.Div(
    [
        sidebar,  
        html.Div(
            className='graph-container',
            children=[
                dbc.Row(
                    className='row',
                    children=[
                        # Left side - Pie Chart and Bubble Chart
                        dbc.Col(
                            width=5,
                            children=[
                                dcc.Graph(id='pie-chart', className='pie-graph'),
                                dcc.Graph(id='bubble-chart', className='bubble-graph'),
                            ]
                        ),
                        # Right side - Choropleth Map
                        dbc.Col(
                            width=7,
                            children=[
                                dcc.Graph(id='choropleth-map', className='choropleth-map'),
                            ]
                        ),
                    ],
                )
            ],
        ),
    ]
)

# --- callbacks ---
@app.callback(
    [Output('pie-chart', 'figure'),
     Output('bubble-chart', 'figure'),
     Output('choropleth-map', 'figure')],
    [Input('year-dropdown', 'value'),
     Input('commune-dropdown', 'value')]
)
def update_insights(selected_year, selected_commune):
    filtered_df = df
    
    # Filter based on the year if a year is selected
    if selected_year:
        filtered_df = filtered_df[filtered_df['Alerte'].dt.year == selected_year]
    
    # Filter based on the commune if a commune is selected
    if selected_commune:
        filtered_df = filtered_df[filtered_df['Commune'] == selected_commune]
    
    # Check filtered dataframe shape
    # print(f"Filtered DataFrame shape: {filtered_df.shape}")
    
    # --- Pie Chart ---
    fire_origin_distribution = filtered_df['Origine de l\'alerte'].value_counts().reset_index()
    fire_origin_distribution.columns = ['Origin', 'Count']
    pie_fig = px.pie(fire_origin_distribution, names='Origin', values='Count', title="Fire Origin Distribution", hole=0.5)
    pie_fig.update_layout(
        template='plotly_dark',
        margin={'t': 50, 'b': 50, 'l': 0, 'r': 50},
        autosize=True
    )
    
    # --- Bubble Chart ---
    dfci_fire_distribution = filtered_df['Code du carreau DFCI'].value_counts().reset_index()
    dfci_fire_distribution.columns = ['DFCI_Code', 'Fire_Count']
    dfci_fire_distribution['Impact'] = dfci_fire_distribution['Fire_Count'] * 10
    bubble_fig = px.scatter(dfci_fire_distribution, x='DFCI_Code', 
                            y='Fire_Count', 
                            size='Impact', color='Fire_Count', 
                            title="Fire Occurrences by DFCI Code", size_max=20)
    bubble_fig.update_layout(
        template='plotly_dark',
        margin={'t': 50, 'b': 50, 'l': 0, 'r': 50},
        autosize=True
    )
    
    # --- Choropleth Map ---
    filtered_gdf = merged.copy()

    # Apply the commune filter if selected
    if selected_commune:
        filtered_gdf = filtered_gdf[filtered_gdf['Commune'] == selected_commune]

    # Check filtered GeoDataFrame shape
    # print(f"Filtered GeoDataFrame shape: {filtered_gdf.shape}")

    # Calculating Population Density (Pop Density: population/area)
    filtered_gdf['Population Intensity'] = filtered_gdf['POPULATION'] / filtered_gdf['SUPERFICIE']

    # Apply logarithmic transformation to the Population Intensity for better visualization
    filtered_gdf['Density'] = np.log1p(filtered_gdf['Population Intensity'])

    # Create the choropleth map with logarithmic scaling for better visual differentiation
    choropleth_fig = px.choropleth(
        filtered_gdf,
        template='plotly_dark',
        geojson=filtered_gdf.geometry.__geo_interface__,
        locations=filtered_gdf.index,
        color='Density',
        hover_name='Commune',
        hover_data=['SUPERFICIE', 'Surface parcourue (m2)', 'POPULATION', 'Population Intensity'],
        color_continuous_scale='Viridis',
        range_color=[filtered_gdf['Density'].min(), filtered_gdf['Density'].max()],
        title="Bouches-du-Rhône Communes & Population Intensity"
    )

    choropleth_fig.update_geos(
        fitbounds="locations",
        visible=False,
        showcoastlines=False,
        projection_type="mercator",
        center={"lat": 43.5, "lon": 5.4},
        projection_scale=3
    )

    choropleth_fig.update_layout(
        autosize=True,
        margin={"t": 50, "b": 20, "l": 20, "r": 20}
    )

    # Return the updated figures (pie, bubble, and choropleth)
    return pie_fig, bubble_fig, choropleth_fig


# 3. --- Trends Layout ---
trends_layout = html.Div(
    [
        sidebar, 
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id='yearly-trends-graph')],
                            className="yearly-trends"
                        ),
                        html.Div(
                            [dcc.Graph(id='monthly-trends-graph')],
                            className="monthly-trends"
                        ),
                    ],
                    className="trends-top-section",
                ),
                html.Div(
                    [dcc.Graph(id='hourly-trends-graph')],
                    className="trends-bottom-section",
                ),
            ],
            className="trends-container",
        ),
    ],
    className="trends-background",
)

# --- Callback for Trends ---
@app.callback(
    [
        Output("monthly-trends-graph", "figure"),
        Output("hourly-trends-graph", "figure"),
        Output("yearly-trends-graph", "figure"),
    ],
    [Input("year-dropdown", "value")],
)
def update_trends(selected_year):
    # Filter data by selected year
    filtered_df = df.copy()
    if selected_year:
        filtered_df = filtered_df[filtered_df["Alerte"].dt.year == selected_year]

    # Group by Month
    monthly_trend = (
        filtered_df.groupby(filtered_df["Alerte"].dt.to_period("M"))
        .size()
        .reset_index(name="Fire Count")
    )
    monthly_trend["Alerte"] = monthly_trend["Alerte"].dt.strftime("%Y-%m")

    # Group by Hour
    hourly_trend = (
        filtered_df.groupby(filtered_df["Alerte"].dt.hour)
        .size()
        .reset_index(name="Fire Count")
    )
    hourly_trend["Hour"] = hourly_trend["Alerte"]

    # Group by Year
    yearly_trend = (
        filtered_df.groupby(filtered_df["Alerte"].dt.year)
        .size()
        .reset_index(name="Fire Count")
    )

    # --- Monthly Trend Plot ---
    monthly_fig = px.line(
        monthly_trend,
        x="Alerte",
        y="Fire Count",
        title="Monthly Fire Alerts",
    )
    monthly_fig.update_layout(
        template="plotly_dark",
        xaxis_title="Month",
        yaxis_title="Fire Count",
        margin={"t": 50, "b": 50, "l": 50, "r": 50},
        showlegend=False,
    )

    # --- Hourly Trend Plot ---
    hourly_fig = px.bar(
        hourly_trend,
        x="Hour",
        y="Fire Count",
        title="Hourly Fire Alerts",
        color="Fire Count",
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    hourly_fig.update_layout(
        template="plotly_dark",
        xaxis_title="Hour of the Day",
        yaxis_title="Number of Fire Alerts",
        margin={"t": 40, "b": 40, "l": 40, "r": 40},
        height=210,
        font=dict(size=10),
        bargap=0.1,
        coloraxis_showscale=False,
        showlegend=False,
    )
    hourly_fig.update_xaxes(tickangle=0, tickfont=dict(size=8), automargin=True)
    hourly_fig.update_yaxes(tickfont=dict(size=8), automargin=True)
    hourly_fig.update_traces(marker=dict(line=dict(width=0.5)))

    # --- Yearly Trend Plot ---
    yearly_fig = px.bar(
        yearly_trend,
        x="Fire Count",
        y="Alerte",
        orientation="h",
        title="Yearly Fire Alerts",
        color="Fire Count",
        color_continuous_scale="Cividis",
    )
    yearly_fig.update_layout(
        template="plotly_dark",
        xaxis_title="Fire Count",
        yaxis_title="Year",
        margin={"t": 50, "b": 50, "l": 50, "r": 50},
        coloraxis_showscale=False,
    )
    yearly_fig.update_traces(showlegend=False)

    return monthly_fig, hourly_fig, yearly_fig


# 4. --- QGIS Layout ---
qgis_mapping_layout = html.Div([
    sidebar, 
    # Embed HTML file (QGIS map)
    # html.Div([
    html.Iframe(
        src='/html/index.html',  
        width="100%",  
        height="100%", 
        style={
            'border': 'none',
            'position': 'absolute',
            'top': '0px',
            'left': '0',
            'right': '0',
            'bottom': '0',
        }
    )
], style={
    'height': 'calc(100vh - 0px)',  
    'width': 'calc(100vw - 265px)',  
    'position': 'absolute',
    'bottom': '0',
    'left': '265px',  
})


# --------------------------------
#  Main Layout
# --------------------------------
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Tracks current pathname
    sidebar,
    toggle_button,
    hidden_sidebar,
    html.Div(id='page-content', className='page-content')
])

@app.callback(
    [Output('hidden-sidebar', 'style'),
     Output('toggle-sidebar', 'style'),
     Output('toggle-sidebar', 'children')],
    [Input('toggle-sidebar', 'n_clicks')],
    [State('hidden-sidebar', 'style')]
)
def toggle_hidden_sidebar(n_clicks, current_style):
    # Default styles
    hidden_sidebar_style = {'left': '-265px', 'transition': 'left 0.3s ease'}
    visible_sidebar_style = {'left': '265px', 'transition': 'left 0.3s ease'}
    toggle_button_default_style = {'left': '245px', 'transition': 'left 0.3s ease'}
    toggle_button_active_style = {'left': '540px', 'transition': 'left 0.3s ease'}

    # Toggle logic
    if current_style and current_style.get('left') == '-265px':
        # Show the hidden sidebar
        return visible_sidebar_style, toggle_button_active_style, "◀️"
    else:
        # Hide the hidden sidebar
        return hidden_sidebar_style, toggle_button_default_style, "▶️"


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return home_layout
    elif pathname == '/trends':
        return trends_layout
    elif pathname == '/insights':
        return insights_layout
    
    elif pathname == '/qgis_mapping':
        return qgis_mapping_layout
 
    return html.Div("Page not found")


# --------------------------------
#  Run the app, trying port 8060 in case of problem
# --------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

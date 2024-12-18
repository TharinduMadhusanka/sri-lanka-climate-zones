import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import streamlit as st

def load_data():
    try:
        # Fixed file paths for local files
        climate_data_path = 'Sri_Lanka_Climate_Data.csv'
        shapefile_path = 'lka_admbnda_adm2_slsd_20220816.shp'

        df = pd.read_csv(climate_data_path)
        country_map = gpd.read_file(shapefile_path)

        # Drop duplicates for cleaner dataset
        df[['latitude', 'longitude']].drop_duplicates()

        # Aggregate data for each location
        climate_data = df.groupby(['latitude', 'longitude']).agg({
            'temperature_2m_max': 'mean',
            'temperature_2m_min': 'mean',
            'precipitation_sum': 'sum',
            'temperature_2m_avg': 'mean'
        }).reset_index()

        # Available features for clustering
        available_features = ['temperature_2m_max',
                              'temperature_2m_min', 'precipitation_sum', 'temperature_2m_avg']

        scaler = StandardScaler()

        # Sidebar feature selection
        selected_features = st.sidebar.multiselect(
            "Select Features for Clustering",
            options=available_features,
            default=['temperature_2m_max']
        )

        if not selected_features:
            st.error("Please select at least one feature for clustering.")
            return None, None, None, None

        # Filter selected features and scale them
        climate_features = climate_data[selected_features]
        scaled_features = scaler.fit_transform(climate_features)

        # KMeans clustering
        n_clusters = st.sidebar.slider(
            "Number of Clusters", min_value=2, max_value=10, value=4)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        climate_data['cluster'] = kmeans.fit_predict(scaled_features)

        # Create Point geometry for geospatial data
        geometry = [Point(lon, lat) for lon, lat in zip(
            climate_data['longitude'], climate_data['latitude'])]
        gdf = gpd.GeoDataFrame(climate_data, geometry=geometry)

        return gdf, country_map, climate_data, selected_features

    except FileNotFoundError as e:
        st.error(f"File not found: {e}")
        st.error(
            "Please ensure 'climate_data_sri_lanka_full.csv' and the Shapefile are in the correct directory.")
        return None, None, None, None
    except Exception as e:
        st.error(f"An unexpected error occurred while loading data: {e}")
        return None, None, None, None

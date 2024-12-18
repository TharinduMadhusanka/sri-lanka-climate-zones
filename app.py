import streamlit as st
import os

os.environ["OMP_NUM_THREADS"] = "2"

from src.load_data import load_data
from src.plotmap import plot_climate_zones

def initialize_session_state():
    if 'plot_boundary' not in st.session_state:
        st.session_state.plot_boundary = False

    if 'show_district_names' not in st.session_state:
        st.session_state.show_district_names = False

    if 'selected_cmap' not in st.session_state:
        st.session_state.selected_cmap = 'Spectral'

def main():
    # Set page configuration
    st.set_page_config(page_title="Climate Zones of Sri Lanka", layout="wide")

    initialize_session_state()

    st.sidebar.header("Visualization Controls")

    # Boundary and district name toggles
    st.session_state.plot_boundary = st.sidebar.checkbox(
        "Plot Boundary", value=st.session_state.plot_boundary)

    st.session_state.show_district_names = st.sidebar.checkbox(
        "Show District Names", value=st.session_state.show_district_names)

    # Colormap selection
    st.session_state.selected_cmap = st.sidebar.selectbox(
        "Select Colormap",
        options=['Spectral', 'viridis', 'plasma',
                 'inferno', 'magma', 'cividis'],
        index=0
    )

    st.title("Sri Lanka Climate Zone Analysis")

    gdf, country_map, climate_data, selected_features = load_data()

    # Check if data is loaded successfully
    if gdf is None or country_map is None:
        st.error("Unable to load data. Please check your files and try again.")
        return

    # Visualization method selection
    visualization_method = st.sidebar.selectbox(
        "Visualization Method",
        options=["Dot (Scatterplot)", "Fill (Colored Districts)",
                 "Interpolated Surface"],
        index=0
    )

    # Interpolation method (only show when Interpolated Surface is selected)
    interpolation_method = 'nearest'
    if visualization_method == "Interpolated Surface":
        interpolation_method = st.sidebar.selectbox(
            "Interpolation Method",
            options=['nearest', 'linear', 'cubic'],
            index=0
        )

    # Generate Map button
    if st.button("Generate Climate Zones Map"):
        plot_buffer = plot_climate_zones(
            gdf, country_map,
            visualization_method,
            interpolation_method,
            selected_features
        )

        if plot_buffer:
            st.image(plot_buffer, use_column_width='auto')

if __name__ == "__main__":
    main()

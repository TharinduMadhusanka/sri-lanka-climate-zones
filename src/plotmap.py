import matplotlib.pyplot as plt
import streamlit as st
import io
import geopandas as gpd

from src.interpolate import interpolate_with_gap_filling


def plot_climate_zones(gdf, country_map, visualization_method, interpolation_method, selected_features):
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 12))

        # Colormap selection
        cmap = plt.cm.get_cmap(st.session_state.selected_cmap)

        # Ensure a valid single feature is selected for plotting
        if not selected_features or len(selected_features) == 0:
            st.error(
                "No feature selected for visualization. Please select at least one feature.")
            return None

        # Use the first selected feature
        feature_to_plot = selected_features[0]

        # Visualization methods
        if visualization_method == "Interpolated Surface":
            # Perform interpolation
            grid_lon, grid_lat, interpolated_values = interpolate_with_gap_filling(
                gdf, country_map, feature_to_plot, interpolation_method
            )

            if grid_lon is not None:
                # Plot interpolated surface
                c = ax.imshow(
                    interpolated_values,
                    extent=(grid_lon.min(), grid_lon.max(),
                            grid_lat.min(), grid_lat.max()),
                    origin='lower',
                    cmap=cmap,
                    alpha=0.7
                )
                cbar = plt.colorbar(c, ax=ax, orientation='vertical',fraction=0.03, pad=0.04)

        elif visualization_method == "Dot (Scatterplot)":
            # Simple scatter plot of the selected feature
            # Plot the country boundary
            country_map.plot(ax=ax, color='lightgray')
            scatter = gdf.plot(ax=ax, column=feature_to_plot, cmap=cmap,
                               legend=True, marker='o', markersize=50, alpha=0.7)

        elif visualization_method == "Fill (Colored Districts)":
            # Merge cluster data with the shapefile for fill-based plotting
            gdf_sjoin = gpd.sjoin(
                gdf, country_map, how='left', predicate='within')
            merged = country_map.merge(
                gdf_sjoin[[feature_to_plot, 'ADM2_EN']], on='ADM2_EN', how='left')
            merged.plot(ax=ax, column=feature_to_plot,
                        cmap=cmap, legend=True, alpha=0.7)

        # Add district names if the checkbox is selected
        if st.session_state.show_district_names:
            for _, row in country_map.iterrows():
                centroid = row.geometry.centroid
                ax.text(centroid.x, centroid.y,
                        row['ADM2_EN'], fontsize=5, ha='center', color='blue')

        if st.session_state.plot_boundary:
            country_map.boundary.plot(ax=ax, linewidth=1.5, edgecolor='black')

        ax.set_title(f'Climate Zones in Sri Lanka ({feature_to_plot})')
        ax.set_axis_off()

        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)

        return buf

    except Exception as e:
        st.error(f"Error generating plot: {e}")
        return None

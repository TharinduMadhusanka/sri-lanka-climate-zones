import numpy as np
from scipy.interpolate import griddata
import rasterio
import rasterio.features
from scipy import ndimage


def interpolate_with_gap_filling(gdf, country_map, selected_feature, interpolation_method='cubic'):
    # Get the country boundaries
    lon_min, lat_min, lon_max, lat_max = country_map.total_bounds

    # Create a denser grid (increased resolution to 500x500)
    grid_lon, grid_lat = np.meshgrid(
        np.linspace(lon_min, lon_max, 500),  # High resolution
        np.linspace(lat_min, lat_max, 500)   # High resolution
    )

    # Prepare input data for interpolation
    input_points = gdf[['longitude', 'latitude']].values
    input_values = gdf[selected_feature].values

    # Initial interpolation
    interpolated_values = griddata(
        points=input_points,
        values=input_values,
        xi=(grid_lon, grid_lat),
        method=interpolation_method
    )

    # Combine all geometries into one using `union_all`
    sri_lanka_boundary = country_map.geometry.union_all()

    # Create a mask for Sri Lanka's boundary
    mask_shape = interpolated_values.shape
    transform = [  # Affine transform for the grid
        (lon_max - lon_min) / mask_shape[1], 0, lon_min,
        0, (lat_max - lat_min) / mask_shape[0], lat_min
    ]

    # Create mask with boundary
    mask = rasterio.features.geometry_mask(
        [sri_lanka_boundary],
        transform=transform,
        out_shape=mask_shape,
        invert=True,
        all_touched=True
    )

    # Identify nan values within the mask
    nan_mask = np.isnan(interpolated_values) & mask

    # Fill methods to try
    if np.any(nan_mask):
        # 1. Nearest neighbor filling
        filled_values = griddata(
            points=input_points,
            values=input_values,
            xi=(grid_lon, grid_lat),
            method='nearest'
        )

        # Replace nan values with nearest neighbor interpolation
        interpolated_values[nan_mask] = filled_values[nan_mask]

        # 2. If still some nans, use scipy's gaussian filter for smooth interpolation
        if np.any(np.isnan(interpolated_values)):
            # Temporarily replace nans with a smoothed version
            temp_values = interpolated_values.copy()

            # Smooth the data
            smooth_values = ndimage.gaussian_filter(np.nan_to_num(temp_values, nan=np.nanmean(temp_values)),
                sigma=10  # Adjust sigma for more or less smoothing
            )

            # Fill remaining nans with smoothed values
            nan_indices = np.isnan(temp_values)
            interpolated_values[nan_indices] = smooth_values[nan_indices]

    # Apply final mask to ensure only Sri Lanka area is shown
    masked_values = np.ma.masked_array(
        interpolated_values,
        mask=~mask
    )

    return grid_lon, grid_lat, masked_values

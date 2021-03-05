"""Module to process data downloaded from the Swiftly API.

The official Swiftly API documentation can be found here:
https://swiftly-dashboard-iframe.docs.stoplight.io/

Contributors: Elliot Huang
Version: 2021-03-02
Latest: https://github.com/BayAreaMetro/dpdutils
"""
# %%
import copy
import pandas as pd

# %%
def speed_map_segs_to_df(seg_list):
    """Return a DataFrame given a list of high resolution segments from the Swiftly Speed Maps API."""
    # Put segment list into DataFrame
    df = pd.DataFrame(seg_list)

    # Seperate the start and end coords from pathLocs
    temp_df = pd.DataFrame(df['pathLocs'].to_list())
    temp_df.rename({0: 'start', 1: 'end'}, axis=1, inplace=True)

    # Put start coords into a dataframe
    start_coords = pd.DataFrame(temp_df['start'].to_list())
    start_coords.columns = start_coords.columns.str.capitalize()
    start_coords = start_coords.add_prefix('start')

    # Put end coords into a dataframe
    end_coords = pd.DataFrame(temp_df['end'].to_list())
    end_coords.columns = end_coords.columns.str.capitalize()
    end_coords = end_coords.add_prefix('end')

    # Drop columns we don't care about
    df = df.drop(['pathLocs', 'toStop', 'fromStop'], axis=1, errors='ignore')

    # Combine the dataframes side by side
    return pd.concat([start_coords, end_coords, df], axis=1)

# %%
def speed_map_segs_to_geojson(seg_list):
    """Return a GeoJSON given a list of high resolution segments from the Swiftly Speed Maps API."""
    # Initialize a new GeoJSON object
    new_geojson = {
        'type': 'FeatureCollection',
        'features': []
    }

    # Dont work on the input list
    seg_list_copy = copy.deepcopy(seg_list)

    # Iterativley build the features of the new GeoJSON object
    for i, seg in enumerate(seg_list_copy):
        # Prepare the feature properties
        del seg['fromStop']
        del seg['toStop']

        # New attribute, can be used to identify segments
        seg['order'] = i

        # Prepare the feature geometry coordinates
        pathLocs = seg.pop('pathLocs')
        coords = [[p['lon'], p['lat']] for p in pathLocs]

        # Construct feature
        new_feature = {
            'type': 'Feature',
            'geometry': {'type': 'LineString', 'coordinates': coords},
            'properties': seg
        }

        # Append feature to the list of features in GeoJSON object
        new_geojson['features'].append(new_feature)

    return new_geojson

# %%

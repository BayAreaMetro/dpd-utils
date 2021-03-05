"""Swiftly Example 1

Use the speed map API endpoint of the Swiftly API with the high resolution parameter
to download data for a given agency, route, date, and time range. Convert the return
object to a pandas dataframe and geopandas object and write the results to disk.

This example requires that you authenticate with your API key, which should be 
stored in a JSON file containing the following: {"key": "<YOUR API KEY>"}

Author: Elliot Huang
"""

# %%
import json
import copy

import pandas as pd

from dpdutils import swiftly

# %%
# get the api key from json
key_path = "./SWIFTLY_API_KEY.json"
api_key = swiftly.api.get_key(key_path)['key']

# make the api call
speed_map_data = swiftly.api.speed_map(
    api_key=api_key, 
    agencyKey='napa-valley', 
    routeKey='29', 
    direction='1', 
    startDate='10-15-2019',
    beginTime="05:00",
    endTime="10:00",
    resolution='hiRes'
)

# here we are only interested in the list of segments
seg_list = speed_map_data['data']['segments']

# %%
# convert the speed map result into a pandas dataframe
speed_map_df = swiftly.datapro.speed_map_segs_to_df(seg_list)

# write the dataframe as csv to disk
speed_map_df.to_csv('napa_route29_dir1.csv', index=False)

# %%
# convert the speed map result into a geojson object
speed_map_geojson = swiftly.datapro.speed_map_segs_to_geojson(seg_list)

# write the full geojson to a file
with open('./napa_route29_dir1.geojson', 'w') as outfile:
    json.dump(speed_map_geojson, outfile)

# %%


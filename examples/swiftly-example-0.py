"""Swiftly Example 0

Use the gps playback API endpoint of the Swiftly API to download data for a given
agency, route, date, and time range. Combine the results into a single dataframe
and write as a csv file.

This example requires that you authenticate with your API key, which should be 
stored in a JSON file containing the following: {"key": "<YOUR API KEY>"}

Author: Elliot Huang
"""

# %%
import pandas as pd

from dpdutils import swiftly

# %%
# define a list of non continous dates
date_ranges = [
    {
        "start_date": "04-01-2019",
        "end_date": "05-31-2019",
        "include_days": [1, 1, 1, 1, 1, 0, 0]
    },

    {
        "start_date": "09-01-2020",
        "end_date": "10-31-2020",
        "include_days": [1, 1, 1, 1, 1, 0, 0]
    },
]

# get formatted dates from a helper function in the module
dates = swiftly.api.get_formatted_dates(date_ranges)

# get the api key from json
key_path = "./SWIFTLY_API_KEY.json"
api_key = swiftly.api.get_key(key_path)["key"]

# make repeated called to the api, storing each result in a list
dfs = []

for d in dates:
    print("Downloading data for date: {}".format(d))
    r = swiftly.api.gps_playback(
        api_key=api_key,
        agencyKey="actransit", 
        route="L", 
        queryDate=d,
    )
    df = pd.DataFrame(r['data']['data'])
    dfs.append(df)

# combine results from repeated api calls into single dataframe, write to csv
final = pd.concat(dfs)
final.to_csv("./actransit_route-L_2019-4-5-9-10.csv", index=False)

# %%

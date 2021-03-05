"""Inrix Roadway Analytics Example 1

Define a roadway analytics report, download the zip file using the Inrix API, 
aggregate from segment to corridor, and write aggregated dataframe to disk.

This example requires that you authenticate with your API credentials, which 
should be stored in a JSON file containing the following:
{
    "email": "<YOUR EMAIL>",
    "password": "<YOUR PASSWORD>"
}

Author: Elliot Huang
"""

# %%
import pandas as pd
import dpdutils.inrix.roadway as ira

# %%
# define the location of the credentials json file
inrix_creds_fp = "./INRIX_CREDS.json"

# define a corridor
corridors = [
    {
        "name" : "sfobb_toll_plaza",
        "direction" : "W",
        "xdSegIds" : [1626760569, 1626681261, 1626639360, 1626752802]
    }
]

# download the corridor report zip file using the api
downloaded_zip = ira.api.download_corridor_report(
    inrix_creds_fp=inrix_creds_fp, 
    corridors=corridors, 
    start_date = "2020-08-01",
    end_date = "2020-08-02",
    granularity=15,
    map_version="2001"
)

# create an object to hold the zip data
inrix_data = ira.datapro.CorridorReportZip()
inrix_data.read_zip(ra_zip=downloaded_zip)

# have the object provide a pandas dataframe
df = inrix_data.segments_to_corridor(
    out_format="wide",
    wide_metric="speed",
    out_dir="./",
    out_fn="corridor_data.csv"
)

# %%
df

# %%

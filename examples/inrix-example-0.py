"""Inrix Roadway Analytics Example 0

Load a roadway analytics report zip file from disk into memory, aggregate from 
segment to corridor, and write aggregated dataframe to disk.

Author: Elliot Huang
"""

# %%
import pandas as pd
import dpdutils.inrix.roadway as ira

# %%
# define the corridor report zip file location
zip_file_dir="./"
zip_file_name="inrix_corridor_report.zip"

# create an object to hold the zip data
inrix_data = ira.datapro.CorridorReportZip()
inrix_data.read_zip(ra_zip=zip_file_dir+zip_file_name)

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

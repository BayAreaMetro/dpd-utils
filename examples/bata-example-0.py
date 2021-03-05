"""BATA Example 0

Reshape compiled traffic volume reports from the Bay Area Toll Authority. The compiled traffic volume 
reports can be found on the S drive in the BATA/Traffic Reports/Compiled Traffic Volumes directory.

Author: Elliot Huang
"""

# %%
from dpdutils import bata

# %%
# Reshape a compiled traffic volume report for a single BATA bridge to long format
sfobb_vols = bata.ctvr_to_long(
    in_dir="./",
    in_fn="San Francisco-Oakland 1-1-14 through 01-2021.xls",
    out_dir="./",  # default None
    out_fn="SFOBB.csv",  # default None
    sum_lanes=False,  # default False
    sum_hours=False,  # default False
)

sfobb_vols

# %%
# Reshape & combine compiled traffic volume reports for multiple BATA bridges to long format
bata_bridge_vols = bata.combine_ctvrs(
    in_dir="./",
    in_fn_dict={
        "antioch": "Antioch 12-1-05 through 01-2021.xls",
        "benicia": "Benicia 12-1-05 through 01-2021.xls",
        "carquinez": "Carquinez 11-1-05 through 01-2021.xls",
        "dumbarton": "Dumbarton 1-1-06 through 01-2021.xls",
        "richmond": "Richmond 12-1-05 through 01-2021.xls",
        "sfobb": "San Francisco-Oakland 1-1-14 through 01-2021.xls",
        "sanmateo": "San Mateo 12-1-05 through 01-2021.xls",
    },
    out_dir="./",  # default None
    out_fn="all_bata_combined.csv",  # default None
    sum_lanes=True,  # default False
    sum_hours=True,  # default False
)

bata_bridge_vols

# %%

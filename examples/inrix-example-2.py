"""Inrix Roadway Analytics Example 2

Confirms that an Inrix Roadway Analytics corridor report zip file data downloaded 
via the API is the same as data downloaded from the web app. 

This example requires that you authenticate with your API credentials, which 
should be stored in a JSON file containing the following:
{
    "email": "<YOUR EMAIL>",
    "password": "<YOUR PASSWORD>"
}

Since this is more of a test and not really an example, consider refactoring this
script into an integration test.

Author: Elliot Huang
"""

# %%
import datetime

import pandas as pd

import dpdutils.inrix.roadway as ira

# %%
def compare_ra_api_dl_agg_to_local(local_zip_fp, inrix_creds_fp):
    """Checks equivalancy of Inrix Roadway Analytics data downloaded from web app vs API.

    Given a zip file downloaded via the web app and saved locally, this function attempts
    to download the same data via the API. Aggregation is then applied to both the local
    and downloaded version, and checked for equivalency. 

    Args:
        local_zip_fp (str): Local path to an Inrix Roadway Analytics corridor .zip file
        downloaded from the web app
        inrix_creds_fp (str): Local path to JSON containing Inrix credentials
    Returns:
        True if the aggregated dataframes are equivalent, False otherwise
    """
    # read and aggregate the local zip file
    local = ira.datapro.CorridorReportZip()
    local.read_zip(ra_zip=local_zip_fp)
    local_agg = local.segments_to_corridor(out_format="long")

    # end date in report contents is always 1 day later, apply correction
    end_date = (
        datetime.datetime.strptime(
            local.report_contents["dateRanges"][0]["end"], "%Y-%m-%d"
        )
        - datetime.timedelta(days=1)
    ).strftime("%Y-%m-%d")

    # download / aggregate data via api using the same report info as local zip
    downloaded_zip = ira.api.download_corridor_report(
        inrix_creds_fp=inrix_creds_fp, 
        corridors=local.report_contents["corridors"], 
        start_date = local.report_contents["dateRanges"][0]["start"],
        end_date = end_date,
        granularity=local.report_contents["granularity"],
        map_version=local.report_contents["mapVersion"]
    )
    downloaded = ira.datapro.CorridorReportZip()
    downloaded.read_zip(downloaded_zip)
    downloaded_agg = downloaded.segments_to_corridor(out_format="long")

    # check data frames for equivalency
    return (local_agg == downloaded_agg).all().all()

# %%
# define location of local inrix corridor report zip file
local_zip_fp = "./inrix_corridor_report.zip"

# define location of inrix credentials
inrix_creds_fp = "./INRIX_CREDS.json"

# should return true
compare_ra_api_dl_agg_to_local(local_zip_fp, inrix_creds_fp)

# %%

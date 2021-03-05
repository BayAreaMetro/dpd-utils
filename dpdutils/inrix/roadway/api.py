"""Module to use the Inrix Roadway Analytics Data Downloader API.

Contributors: Elliot Huang
Version: 2021-03-02
Latest: https://github.com/BayAreaMetro/dpdutils
"""

# %%
import json
import time

import requests

# %%
class InrixTimeout(Exception):
    """Exception for a timeout caused by something Inrix related."""
    pass

# %%
def get_creds(inrix_creds_fp):
    """Read and return INRIX credential information from JSON file.
    
    JSON should contain {"email": "<YOUR EMAIL>", "password": "<YOUR PASSWORD"}
    """
    with open(inrix_creds_fp, "r") as f:
        inrix_creds = json.load(f)

    if ("email" not in inrix_creds.keys()) or ("password" not in inrix_creds.keys()):
        msg = (
            f'Cannot read JSON "{inrix_creds_fp}". ' 
            f'JSON should contain {{"email": "<YOUR EMAIL>", "password": "<YOUR PASSWORD"}}'
        )
        raise ValueError(msg)

    return inrix_creds

# %%
def get_access_token(inrix_creds):
    """Get access token to use with Inrix Roadway Analytics Data Downloader API.
    
    Args:
        inrix_creds (json)
    Returns:
        The accessToken from the API response
        Note the API response contains other types of tokens, but are not used here
    More info: 
        See Step 1 of the INRIX Roadway Analytics Data Downloader API documentation
    """
    endpoint = "https://roadway-analytics-api.inrix.com/v1/auth"
    r = requests.post(endpoint, json=inrix_creds)
    r.raise_for_status()
    return r.json()["result"]["accessToken"]["token"]

# %%
def create_new_corridor_report(
    access_token, start_date, end_date, corridors, granularity, map_version
):
    """Create new INRIX Roadway Analytics report for specified corridor(s).

    Args:
        access_token (str): Get from seperate endpoint
        start_date (str): "YYYY-MM-DD"
        end_date (str): "YYYY-MM-DD"
        corridors (list of dict): Each dict is a corridor definition with the format:
            {
                "name" : <corridor name (string)>,
                "direction" : <corridor direction (single char from N, S, W, E)>,
                "xdSegIds" : <xd segment ids (list of int)>
            }
        granularity (int): 1, 5, 15, or 60
        map_version (str): Version the Inrix XD map segmentation "1902", "2001", etc
    Returns:
        The ID of the newly created report
    More info:
        See Step 2 of the INRIX Roadway Analytics Data Downloader API documentation
    """
    endpoint = "https://roadway-analytics-api.inrix.com/v1/data-downloader"
    auth_header = {"Authorization": f"Bearer {access_token}"}

    # this report definition is similar to reportContents.json found in the 
    # zip file of any downloaded report
    report_def = {
        "unit": "IMPERIAL", 
        "fields": [
            "LOCAL_DATE_TIME", 
            "XDSEGID", 
            "UTC_DATE_TIME", 
            "SPEED", 
            "NAS_SPEED", 
            "REF_SPEED", 
            "TRAVEL_TIME", 
            "CVALUE", 
            "SCORE", 
            "CORRIDOR_REGION_NAME", 
            "CLOSURE"
        ], 
        "corridors" : corridors,
        "timezone": "America/Los_Angeles",
        "dateRanges": [{
            "start": start_date, 
            "end": end_date, 
            "daysOfWeek": [1, 2, 3, 4, 5, 6, 7]
        }], 
        "mapVersion": str(map_version), 
        "reportType": "DATA_DOWNLOAD", 
        "granularity": granularity, 
        "emailAddresses": [],
        "includeClosures": True
    }

    r = requests.post(endpoint, json=report_def, headers=auth_header)
    r.raise_for_status()
    return r.json()["reportId"]

# %%
def check_report_status(access_token, report_id):
    """Checks the status of an Inrix Roadway Analytics report.
    
    Args:
        access_token (str): Get from seperate endpoint
        report_id (str): The report id to check the status for
    Returns:
        A JSON object describing the status of the report
    More info:
        See Step 3 of the INRIX Roadway Analytics Data Downloader API documentation
    """
    endpoint = f"https://roadway-analytics-api.inrix.com/v1/report/status/{report_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(endpoint, headers=auth_header)
    r.raise_for_status()
    return r.json()

# %%
def wait_for_report_completion(access_token, report_id):
    """Waits for the Inrix report to be ready, checking periodically up to a maximum.

    Args:
        access_token (str): Get from seperate endpoint
        report_id (str): The report id to wait for
    Returns:
        None
    Raises:
        InrixTimeout if the max wait time is reached
    """
    start = time.time()
    elapsed = time.time() - start
    max_wait = 60 * 10
    check_interval = 10
    
    report_status = check_report_status(access_token, report_id)
    while report_status["state"] != "COMPLETED":
        print(f"Time elapsed: {elapsed}")
        if elapsed >= max_wait:
            raise InrixTimeout(
                f"Inrix report generation took over {max_wait/60} minutes"
            )
        else:
            time.sleep(check_interval)
            report_status = check_report_status(access_token, report_id)
            elapsed = time.time() - start
    print(f"Time elapsed: {elapsed}")

# %%
def get_report_data(access_token, report_id):
    """Gets information on the report.
    
    Args:
        access_token (str): Get from seperate endpoint
        report_id (str): The report id to get the data for
    Returns:
        A url where the report can be downloaded
    More info:
        See Step 4 of the INRIX Roadway Analytics Data Downloader API documentation
    """
    endpoint = f"https://roadway-analytics-api.inrix.com/v1/data-downloader/{report_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(endpoint, headers=auth_header)
    r.raise_for_status()
    return r.json()

# %%
def get_report_bytes(report_data):
    """Downloads report described by report_data, returns as bytes object."""
    if len(report_data["urls"]) > 1:
        # not sure when this would ever be the case, need to investigate
        raise NotImplementedError("Report contains multiple urls")
    r = requests.get(report_data["urls"][0])
    return r.content

# %%
def download_corridor_report(
    inrix_creds_fp, corridors, start_date, end_date, granularity, map_version
):
    print("Authenticating with Inrix...")
    inrix_creds = get_creds(inrix_creds_fp)
    access_token = get_access_token(inrix_creds)

    print("Creating new Inrix report...")
    report_id = create_new_corridor_report(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        corridors=corridors,
        granularity=granularity,
        map_version=map_version
    )
    print(f"New report created with id: '{report_id}'")

    print("Waiting for report to finish processing...")
    wait_for_report_completion(access_token, report_id)
    print("Inrix report ready for download")

    print("Downloading report from Inrix...")
    report_data = get_report_data(access_token, report_id)
    inrix_zip = get_report_bytes(report_data)
    print("Report downloaded from Inrix")

    return inrix_zip

# %%

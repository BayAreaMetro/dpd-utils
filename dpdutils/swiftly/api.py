"""Module to interface with the Swiftly API.

The official Swiftly API documentation can be found here:
https://swiftly-dashboard-iframe.docs.stoplight.io/

Contributors: Elliot Huang
Version: 2021-03-02
Latest: https://github.com/BayAreaMetro/dpdutils
"""
# %%
import time
import json

import requests
import pandas as pd

# %%
def get_key(key_path):
    """Read and return Swiftly API key from JSON file.
    
    JSON should contain {"key": "<YOUR API KEY>"}
    """
    with open(key_path, "r") as f:
        api_key = json.load(f)

    if "key" not in api_key.keys():
        msg = f'Cannot read JSON "{key_path}". JSON should contain {{"key": "<YOUR API KEY>"}}'
        raise ValueError(msg)

    return api_key

# %%
def get_formatted_dates(date_ranges):
    """Returns list of dates specified by date_ranges, formtted for Swiftly API use.

    date_ranges is a list of dict, with each dict specifying a range of dates
    in string format. sample dict for Tue/Wed/Thu in Sep/Oct:
    {
        "start_date": "09-01-2019",
        "end_date": "10-31-2019",
        "include_days": [0, 1, 1, 1, 0, 0, 0]
    }
    """
    final_date_list = []

    for date_range in date_ranges:
        timestamp_list = pd.bdate_range(
            start=date_range["start_date"], 
            end=date_range["end_date"], 
            weekmask=date_range["include_days"], 
            freq="C"
        ).to_list()

        final_date_list += [ts.strftime("%m-%d-%Y") for ts in timestamp_list]

    return final_date_list

# %%
def make_api_call(api_key, url, params):
    """Makes a Swiftly API call, returns json response.

    This function makes an API call to the endoint at 'url' and returns the JSON response.
    Another function should prepare the URL and query parameters.

    The official Swiftly API documentation can be found here:
    https://swiftly-dashboard-iframe.docs.stoplight.io/

    Args:
        url (string): The Swiftly API endpoint
        params (dict): Query parameters for the call

    Returns:
        The API response json

    Raises:
        requests.exceptions.HTTPError: If there is an HTTP error
        ValueError: If the API reponse status code is not 200, 4XX, or 5XX
    """
    headers = {'Authorization' : api_key}

    keep_trying = True
    attempt_number = 0
    max_attempts = 10

    while keep_trying:
        attempt_number += 1
        r = requests.get(url=url, params=params, headers=headers)
        if r.status_code == 200:
            keep_trying = False
        elif r.status_code == 429:
            # wait if we exceed the swiftly api usage limit
            if attempt_number < max_attempts:
                time.sleep(1000)
            else:
                r.raise_for_status()
        else:
            # raise http error if one occured. if something else occured,
            # then just raise a ValueError with whatever the status code is. 
            # TODO: handle response codes that are not 200, 4XX, or 5XX.
            r.raise_for_status()
            msg = "Unhandeled response status code: {}".format(r.status_code)
            raise ValueError(msg)
    
    return r.json()

# %%
def gps_playback(
    api_key, agencyKey, queryDate, route=None, vehicle=None, beginTime=None, endTime=None
):
    """Builds and makes a call for the GPS Playback enpoint in the Swiftly API.

    Caller responsible for ensuring parameters conform with acepted API query parameters.

    See below for documentation:
    https://swiftly-dashboard-iframe.docs.stoplight.io/gps-playback/getgpsplaybackagencykey
    """             
    params = {
        'api_key': api_key,
        'agencyKey': agencyKey,
        'queryDate': queryDate,
        'route': route,
        'vehicle': vehicle,
        'beginTime': beginTime,
        'endTime': endTime
    }

    gps_playback_url = f'https://api.goswift.ly/gps-playback/{agencyKey}'

    r_json = make_api_call(api_key=api_key, url=gps_playback_url, params=params)

    return r_json

# %%
def speed_map(
    api_key,
    agencyKey,
    routeKey,
    direction,
    startDate,
    endDate=None,
    beginTime=None,
    endTime=None,
    daysOfWeek=None,
    excludeDates=None,
    format=None,
    resolution=None
):
    """Builds and makes a call for the Speed Map enpoint in the Swiftly API.

    Caller responsible for ensuring parameters conform with acepted API query parameters.

    See below for documentation:
    https://swiftly-dashboard-iframe.docs.stoplight.io/speed-map/getspeedmapagencykeyrouteroutekey
    """
    params = {
        'api_key': api_key,
        'agencyKey': agencyKey,
        'routeKey': routeKey,
        'direction': direction,
        'startDate': startDate,
        'endDate': endDate,
        'beginTime': beginTime,
        'endTime': endTime,
        'daysOfWeek': daysOfWeek,
        'excludeDates': excludeDates,
        'format': format,
        'resolution': resolution
    }

    speed_map_url = f'https://api.goswift.ly/speed-map/{agencyKey}/route/{routeKey}'

    r_json = make_api_call(api_key=api_key, url=speed_map_url, params=params)

    return r_json

# %%

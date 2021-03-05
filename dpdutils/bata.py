"""Module to process traffic data from the Bay Area Toll Authority.

Contributors: Elliot Huang
Version: 2021-03-02
Latest: https://github.com/BayAreaMetro/dpdutils
"""

# %%
import pandas as pd

# %%
def ctvr_to_long(
    in_dir, in_fn, out_dir=None, out_fn=None, sum_lanes=False, sum_hours=False
):
    """Reshapes the compiled traffic volume report BATA xls file into long table format.
    
    The compiled traffic volume reports can be found on the S drive, in the 
    BATA/Traffic Reports/Compiled Traffic Volumes directory.

    The long format is good for visualizing in Tableau.

    Args:
        in_dir (str): Directory of the input file.
        in_fn (str): File name of the input file.
        out_dir (str): Directory of the output file. The default is None, indicating that
            an output file should not be written.
        out_fn (str): File name of the output file. The default is None, indicating that
            an output file should not be written.
        sum_lanes (bool): BATA data is provided on a per lane basis. This flag indicates 
            whether or not the output should have all lanes aggregated (summed) together.
        sum_hours (bool): BATA data is provided on a per hour basis. This flag indicates 
            whether or not the output should have all hours aggregated (summed) together 
            (i.e. daily volume)
    Returns:
        Dataframe of compiled traffic volume report data for a single bridge in long format.
    """
    # Read BATA file
    in_path = in_dir + in_fn

    # Read in all sheets
    sheets = pd.read_excel(in_path, sheet_name=None)

    # Standardize (capitalize) all the sheet names
    # Necessary since the capitalization varies between files
    sheets = {k.upper(): v for k, v in sheets.items()}

    # Get the daily by hour by lane sheet
    data = sheets['DAILY BY HOUR BY LANE']
    
    # Clean rows and columns
    data.dropna(subset=["Date"], axis=0, inplace=True)

    if len(data.columns) > 29:
        data = data.iloc[:, 0:29]
    
    # Known columns in the data
    time_cols = [
        "0000-0100",
        "0100-0200",
        "0200-0300",
        "0300-0400",
        "0400-0500",
        "0500-0600",
        "0600-0700",
        "0700-0800",
        "0800-0900",
        "0900-1000",
        "1000-1100",
        "1100-1200",
        "1200-1300",
        "1300-1400",
        "1400-1500",
        "1500-1600",
        "1600-1700",
        "1700-1800",
        "1800-1900",
        "1900-2000",
        "2000-2100",
        "2100-2200",
        "2200-2300",
        "2300-2400",
    ]

    other_cols = ["Date", "Day", "Lane ID"]

    # Reshape data
    data = data[other_cols + time_cols]
    data = data.melt(
        id_vars=other_cols, value_vars=time_cols, var_name="Hour", value_name="Volume"
    )

    # Create timestamp index
    # Each hour timestamp includes 1 extra second, to avoid a bug where the time portion
    # of midnight timestamps were being ignored
    data["Timestamp"] = pd.to_datetime(
        data["Date"].astype("str") + " " + data["Hour"].str.slice(stop=4) + "01"
    )

    # Aggregation logic
    if not sum_lanes and not sum_hours:
        # No aggregation
        data = data[["Timestamp", "Lane ID", "Volume"]]
    elif sum_lanes and not sum_hours:
        # Sum lanes together
        data = data.groupby([data["Timestamp"]]).sum()["Volume"].reset_index()
    elif not sum_lanes and sum_hours:
        # Sum hours together
        data = data.groupby([data["Timestamp"].dt.date, "Lane ID"]).sum().reset_index()
    elif sum_lanes and sum_hours:
        # Sum lanes and hours together
        data = data.groupby([data["Timestamp"].dt.date]).sum()["Volume"].reset_index()
    # Write to disk if desired
    if (out_fn is not None) and (out_dir is not None):
        out_path = out_dir + out_fn
        data.to_csv(out_path, index=False)
    return data

# %%
def combine_ctvrs(
    in_dir, in_fn_dict, out_dir=None, out_fn=None, sum_lanes=False, sum_hours=False
):
    """Combines compiled traffic volume reports for several bridges into a single long table. 

    Args:
        in_fn_dict: A dict of bridge names and the filenames of the BATA compiled volume report.

    Returns:
        Dataframe of compiled traffic volume report data for multiple bridges in long format.
    """
    # Store dataframes of the various bridges
    bridge_dfs = []

    # Process each bridge
    for bridge_name, bridge_fn in in_fn_dict.items():
        print("Processing: {}".format(bridge_name))
        cur_bridge = ctvr_to_long(
            in_dir=in_dir, in_fn=bridge_fn, sum_lanes=sum_lanes, sum_hours=sum_hours
        )
        cur_bridge["Bridge Name"] = bridge_name
        bridge_dfs.append(cur_bridge)
    result = pd.concat(bridge_dfs)

    # Write to disk if desired
    if (out_fn is not None) and (out_dir is not None):
        out_path = out_dir + out_fn
        result.to_csv(out_path, index=False)

    return result

# %%

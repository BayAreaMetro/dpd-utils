"""Module to assist with working with Inrix Roadway Analytics data.

Contributors: Elliot Huang
Version: 2021-03-02
Latest: https://github.com/BayAreaMetro/dpdutils
"""
# %%
import zipfile
import json
import io
import pathlib

import pandas as pd

# %%
class CorridorReportZip(object):
    """Class to manage data from the Inrix Roadway Analytics product.
    
    This class is intended to work with Inrix corridor data downloaded as
    a zip file via the Inrix Roadway Analytics product from both the data
    downloader web app or API. 
    """
    def __init__(self):
        self.ra_zip = None
        self.data = None
        self.metadata = None
        self.report_contents = None
        
    def __load_data(self):
        """Load data.csv from zip file into memory as a pandas dataframe."""
        with zipfile.ZipFile(self.ra_zip, "r") as z:
            zip_root = z.namelist()[0]
            target = f"{zip_root}data.csv"
            with z.open(target) as data_csv:
                self.data = pd.read_csv(data_csv)

    def __load_metadata(self):
        """Load metadata.csv from zip file into memory as a pandas dataframe."""
        with zipfile.ZipFile(self.ra_zip, "r") as z:
            zip_root = z.namelist()[0]
            target = f"{zip_root}metadata.csv"
            with z.open(target) as metadata_csv:
                self.metadata = pd.read_csv(metadata_csv)

    def __load_report_contents(self):
        """Load reportContents.json from zip file into memory as a dictionary."""
        with zipfile.ZipFile(self.ra_zip, "r") as z:
            zip_root = z.namelist()[0]
            target = f"{zip_root}reportContents.json"
            with z.open(target) as report_contents_json:
                self.report_contents = json.load(report_contents_json)

    def read_zip(self, ra_zip):
        """Load data, metadata, and reportContents from zip file into memory.
        
        Args:
            ra_zip: Can be a:
                path to a file (str)
                a file-like object
                a path-like object
                a bytes object containing the in memory zip file
        Returns:
            bool indicating whether or not the load was successful
        """
        # some housekeeping, since we are allowing ra_zip to be a file-like OR bytes
        if isinstance(ra_zip, bytes):
            ra_zip = io.BytesIO(ra_zip)
        else:
            ra_zip = pathlib.Path(ra_zip)
            if not ra_zip.exists():
                raise FileNotFoundError(f"The zip file {ra_zip} does not exist")
        
        self.ra_zip = ra_zip
        
        try:
            self.__load_data()
            self.__load_metadata()
            self.__load_report_contents()
        except FileNotFoundError:
            return False
        except Exception:
            raise

    def write_zip(self, out_path):
        """Writes the zip file to disk."""
        if self.ra_zip is not None:
            with open(out_path, "wb") as f:
                f.write(self.ra_zip)

    def __get_format_data_for_agg(self):
        """Formats the data dataframe to prepare for aggregation."""
        data_formatted = self.data.copy()
        # Strip timezone component and convert to datetime
        data_formatted["Timestamp"] = pd.to_datetime(
            data_formatted["Date Time"].str.slice(start=0, stop=-6)
        )

        # 1:00 AM will be repeated in the fall when daylight savings time ends
        # 1:00 AM will be skipped in the spring when daylight savings time starts
        # Since this time period is generally not useful for traffic analysis
        # we drop the repeated hour and ignore the skipped hour
        data_formatted.drop_duplicates(subset=["Timestamp", "Segment ID"], inplace=True)

        # Create time interval and date columns
        data_formatted["Time Interval"] = (
            data_formatted["Timestamp"].dt.time.astype("str").str.slice(stop=5)
        )
        data_formatted["Date"] = data_formatted["Timestamp"].dt.date.astype("str")

        keep_cols = [
            "Corridor/Region Name",
            "Date",
            "Time Interval",
            "Segment ID",
            "Travel Time(Minutes)",
        ]
        data_formatted = data_formatted[keep_cols]

        return data_formatted

    def __create_data_agg(self):
        """Aggregates and filters formatted data."""
        data_formatted = self.__get_format_data_for_agg()
        gb_cols = ["Corridor/Region Name", "Date", "Time Interval"]
        data_agg = data_formatted.groupby(gb_cols).sum()

        for corridor in self.report_contents["corridors"]:
            # information about corridor from report contents
            corridor_segs = corridor["xdSegIds"]
            corridor_name = corridor["name"]

            # metadata associated with specific corridor only
            mask = self.metadata["Segment ID"].isin(corridor_segs)
            corridor_metadata = self.metadata[mask]
            
            # determine length and segment count of corridor
            length = corridor_metadata["Segment Length(Miles)"].sum()
            seg_count = len(corridor_segs)
            
            # add calculated stuff to dataframe
            data_agg.loc[(corridor_name,), "Corridor Length(Miles)"] = length
            data_agg.loc[(corridor_name,), "Segment Count"] = seg_count

        # dataframe that counts the number of segments with travel time data
        seg_count_alt = data_formatted.groupby(gb_cols).count()
        seg_count_alt.rename({"Travel Time(Minutes)" : "alt_count"}, axis=1, inplace=True)

        # keep only records with full segment count
        mask = data_agg["Segment Count"] == seg_count_alt["alt_count"]
        data_agg = data_agg[mask]

        # calcualte speed from travel time and corridor length (harmonic mean)
        data_agg["Speed(miles/hour)"] = (
            data_agg["Corridor Length(Miles)"] / 
            data_agg["Travel Time(Minutes)"] * 60
        )

        return data_agg

    def segments_to_corridor(
        self,
        out_format="long",
        wide_metric=None,
        out_dir=None,
        out_fn=None,
    ):
        """Aggregates the Inrix Roadway Analytics data from segment level to corridor level.
        
        When you download Inrix data using the Roadway Analytics product, metrics are 
        provided at the segment level. This function aggregates data from the segment level 
        to get corridor level metrics.

        Args:
            zip_file_dir (str): The directory of the Inrix Roadway Analytics .zip file

            zip_file_name (str): The file name of the Inrix Roadway Analytics .zip file

            out_format (str): 'wide' or 'long'. Defines what the desired return format should be.
                'long' format: single column called 'Time Interval' with values 00:00, 01:00,...
                'wide' format: seperate column for each time intervals 00:00, 01:00,...
            
            wide_metric (str): If out_format is 'wide', must specify 'speed' or 'travel_time'
            
            out_dir (str): The directory to write the output dataframe
            
            out_fn (str): The file name to write the output dataframe

        Returns:
            final (dataframe): Inrix speed data aggregated at the corridor level
        """
        # check input values of out_format, wide_metric
        if not ((out_format == "wide") or (out_format == "long")):
            msg = f"out_format is '{out_format}', should be 'wide' or 'long'"
            raise ValueError(msg)
        if out_format == "wide":
            if not ((wide_metric == "speed") or (wide_metric == "travel_time")):
                msg = f"wide_metric is '{out_format}', should be 'speed' or 'travel_time'"
                raise ValueError(msg)

        # format and aggregate Inrix data
        data_agg = self.__create_data_agg()

        # reshape as desired
        if out_format == "wide":
            if wide_metric == "speed":
                final = data_agg.reset_index().pivot_table(
                    index=["Corridor/Region Name", "Date"],
                    columns="Time Interval",
                    values="Speed(miles/hour)",
                )
            elif wide_metric == "travel_time":           
                final = data_agg.reset_index().pivot_table(
                    index=["Corridor/Region Name", "Date"],
                    columns="Time Interval",
                    values="Travel Time(Minutes)",
                )
            else:
                msg = f"wide_metric is '{out_format}', should be 'speed' or 'travel_time'"
                raise ValueError(msg)
        elif out_format == "long":
            keep_cols = ["Speed(miles/hour)", "Travel Time(Minutes)"]
            final = data_agg[keep_cols]
        else:
            msg = f"out_format is '{out_format}', should be 'wide' or 'long'"
            raise ValueError(msg)
        
        # add day of week column
        final = final.reset_index()
        final.insert(
            loc=2,
            column="Day of Week",
            value=pd.to_datetime(final["Date"]).dt.strftime("%A"),
        )

        # write to disk if desired
        if (out_fn is not None) and (out_dir is not None):
            out_path = out_dir + out_fn
            final.to_csv(out_path, index=False)
        
        return final

# %%

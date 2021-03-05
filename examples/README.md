# Examples

## BATA
**bata-example-0.py**
- Demonstrates how to aggregate one or more BATA compiled traffic volume reports. The compiled traffic volume reports can be found on the S drive in the BATA/Traffic Reports/Compiled Traffic Volumes directories (requires MTC VPN access).

## Inrix
**inrix-example-0.py**
- Demonstrates how to aggregate an Inrix Roadway Analytics Corridor Report zip file from the segment level to the corridor level.

**inrix-example-1.py**
- Demonstrates use of the Inrix Roadway Analytics Data Downloader API. 

**inrix-example-2.py**
- More of a test than an example, shows how data downloaded from the Inrix Roadway Analytics Data Downloader API is identical to the data that can be downloaded using the Inrix Roadway Analytics web application.

## Swiftly
**swiftly-example-0.py**
- Demonstrates how to use the Swiftly GPS Playback API endpoint to download data over a discontinuous date range.

**swiftly-example-1.py**
- Demonstrates how to use the Swiftly High Resolution Speed Map API endpoint to download data. Then uses the data processing module in this package to convert the data into a dataframe and geojson object.

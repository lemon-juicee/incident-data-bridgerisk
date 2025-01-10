import numpy as np
import pandas as pd
from pathlib import Path
from gmc import Generic_Mask_Filter

# Code written by Lemon Doroshow
def csvgen(path, MMSI, output=False):
    """csvgen() generates a csv of a ship's longitude, latitude, and datetime (in UTC)
    Parameters:
    path = The date of an AIS csv file; ex: for the file AIS_2018_12_31.csv, path = '2018_12_31' in YYYY_MM_DD format
        type = str
    MMSI = The MMSI of the ship in question
        type = str (returns an empty dataframe if MMSI is entered as an int or float)"
    output = Where to return the csv file and its name, defaults to the data folder with the name 'coordinates_' + path + '.csv' 
        type = str
    Returns:
    csv file in a given path with a given name"""

    # Set up output path
    if output:
        output = output
    else:
        output='data/coordinates_' + path + '.csv'

    # Import filtered AIS data
    data = Generic_Mask_Filter(("data/AIS_" + path + '.csv'), MMSI=[MMSI])

    # Adjust time to compatible format for ArcGIS
    times_adjusted=[x.strftime('%c') for x in  pd.to_datetime(data["BaseDateTime"])]
    
    # Convert data to pd.DataFrame
    mapped_data = {'longitude':data['LON'], 'latitude':data['LAT'], 'time':times_adjusted}
    mapped_df = pd.DataFrame(mapped_data)
    mapped_df = mapped_df.sort_values('time')

    # Export csv file
    mapped_df.to_csv(path_or_buf=output, index=False)

csvgen('2018_12_31', '367552070', output='data/coordinates_charleshuan.csv')
csvgen('2019_01_03', '369371000', output='data/coordinates_ronniemurph.csv')
csvgen('2019_01_14', '367638020', output='data/coordinates_randyeckstein.csv')
csvgen('2021_01_02', '366254000', output='data/coordinates_kapenajackyoung.csv')
csvgen('2021_01_07', '477288000', output='data/coordinates_oceanprincess.csv')
csvgen('2022_01_05', '636017782', output='data/coordinates_orpheus.csv')
csvgen('2022_01_06', '367103180', output='data/coordinates_jacksonplatte.csv')
csvgen('2022_01_15', '366973130', output='data/coordinates_malaga.csv')
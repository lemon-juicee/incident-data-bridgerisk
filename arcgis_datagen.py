import pandas as pd
import numpy as np
from tools import Generic_Mask_Filter, pos_angle, true_difference

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

    # Adjust times and speeds over ground, calculate angle differences
    times_adjusted=[x.strftime('%c') for x in  pd.to_datetime(data["BaseDateTime"])]
    sogs = [np.nan if sog >= 102.3 else sog for sog in [sog + 102.4 if sog < 0 else sog for sog in data['SOG']]]
    angle_diffs = [np.nan if cog == 360.0 or heading == 511.0 else true_difference(pos_angle(cog),pos_angle(heading)) for cog, heading in zip([cog + 409.6 if cog < 0 else cog for cog in data['COG']], data['Heading'])]

    # Convert data to pd.DataFrame
    mapped_data = {'longitude':data['LON'], 'latitude':data['LAT'], 'time':times_adjusted, 'SOG':sogs, 'Angle Difference':angle_diffs}
    mapped_df = pd.DataFrame(mapped_data)
    mapped_df = mapped_df.sort_values('time')

    # Export csv file
    mapped_df.to_csv(path_or_buf=output, index=False)
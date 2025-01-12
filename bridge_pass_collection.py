import numpy as np
import pandas as pd
from gmc import Generic_Mask_Filter

def bridge_reader(path):
    """
    bridge_reader() imports a pre-made csv including all of the AIS data points before and after a ship passes under a ship
    Parameters:
    path = the bridge csv file's path - MUST BE a csv file pre-compiled from our GitHub repo
        type = str
    Returns
    initials = pandas dataframe containing the AIS datapoints before each pass
        type = pandas.DataFrame
    finals = pandas dataframe containing the AIS datapoints after each pass
        type = pandas.DataFrame
    """
    # Import csv
    df = pd.read_csv(path, sep=',', header=0, on_bad_lines="skip")

    # Remove duplicated heading rows
    df = df[df['MMSI'] != 'MMSI']
    df.reset_index(drop=True, inplace=True)

    # Define dataframe objects for before and after each pass
    passes = pd.DataFrame({'MMSI':df['MMSI'], 'BaseDateTime':df['BaseDateTime']})
    initials = passes[passes.index % 2 == 0]
    finals = passes[passes.index % 2 == 1]

    return initials, finals

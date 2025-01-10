import numpy as np
import pandas as pd
from gmc import Generic_Mask_Filter

def bridge_reader(path):
    """
    bridge_reader() imports a pre-made csv including all of the passes under a ship, as rendered in our GitHub repo
    Parameters:
    path = the bridge csv file's path
        type = str
    Returns
    df = pandas dataframe containing the AIS datapoints contained in the csv
        type = pandas.DataFrame
    """

    # Import csv
    # Code is largely similar to Generic_Mask_Filter as the AIS data is in similar formats
    df = pd.read_csv(path, sep=',', header=0, dtype={"Heading": "Int64", 
                                                               "VesselName": str,
                                                               "IMO":str,
                                                               "MMSI":str, #Technically this should be an integer, but some files accidentally insert an alphanumeric character, causing a ValueError
                                                               "LAT":np.float64,
                                                               "LON":np.float64,
                                                               "SOG":np.float64,
                                                               "Heading":"Int64",
                                                               "COG":np.float64,
                                                               "IMO":str,
                                                               "CallSign":str,
                                                               "VesselType":"Int64",
                                                               "Status":"Int64",
                                                               "Length":"Int64",
                                                               "Width":"Int64",
                                                               "Cargo":"Int64",
                                                               "Draft":np.float64,
                                                               "TransceiverClass":str,
                                                               "TranscieverClass":str}, on_bad_lines="skip")
    

    # Remove duplicated heading rows
    df = df[df['MMSI'] != 'MMSI']

    return df
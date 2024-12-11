import numpy as np
import pandas as pd
from pathlib import Path

# Generic_Mask_Filter() written by Diran Jimenez
def Generic_Mask_Filter(file_path, MMSI=False, BaseDateTime=False, LAT=False, LON=False, SOG=False, COG=False,
                        Heading=False, VesselName = False, IMO = False, CallSign = False, VesselType = False,
                        Status = False, Length = False, Width = False, Draft = False, Cargo = False, TransceiverClass = False):
    """
    Parameters
    ----------
    file_path : string
        This string should point to a CSV File of AIS Broadcast Data you wish to filter.
    ALL OTHER PARAMETERS: List
       
        Each parameter corresponds to a column of AIS Broadcast Data
       
        All values to be checked must be passed as a list, even if it is a
            single value. This allows the function to check each column for
            multiple values
       
        The data assumes the "and" condition between all columns, and the
            "or" condition between values in a column.
           
        EX:
            Generic_Mask_Filter(MMSI = [12345], Status = [2]) will return
            broadcasts that have MMSI = 12345 & Status = 2
       
        EX:
            Generic_Mask_Filter(MMSI = [12345, 99999]) will return broadcasts
            that have MMSI = 12345 || MMSI = 99999
                Note that the "or" condition is denoted with "||" by pandas and numpy
       
    Returns
    -------
    df : DataFrame
        A DataFrame that has data which satisfies all criterion passed as input
        conditions.

    """
    # locals() creates a dictionary containing all local variables
    conditions = locals()
    del conditions["file_path"]
        # The only variable not tied to a condition is the file_path

    df = pd.read_csv(file_path, sep=',', header=0, dtype={"Heading": "Int64",
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
   
    # Apply each condition to the DataFrame
    for column, requirements in conditions.items():
        if requirements:
            df = df.loc[df[column].isin(requirements)]

    return df

# Code from here written by Lemon Doroshow
def csvgen(path, MMSI, output=False):
    if output:
        output = output
    else:
        output='data/coordinates_' + path + '.csv'

    data = Generic_Mask_Filter(("data/AIS_" + path + '.csv'), MMSI=[MMSI])

    times_adjusted=[x.strftime('%c') for x in  pd.to_datetime(data["BaseDateTime"])]
    
    mapped_data = { 'longitude':data['LON'], 'latitude':data['LAT'], 'time':times_adjusted}
    mapped_df = pd.DataFrame(mapped_data)

    mapped_df.to_csv(path_or_buf=output, index=False)

csvgen('2018_12_31', '367552070', output='data/coordinates_charleshuan.csv')
csvgen('2019_01_03', '369371000', output='data/coordinates_ronniemurph.csv')
csvgen('2019_01_14', '367638020', output='data/coordinates_randyeckstein.csv')
csvgen('2021_01_02', '366254000', output='data/coordinates_kapenajackyoung.csv')
csvgen('2021_01_07', '477288000', output='data/coordinates_oceanprincess.csv')
csvgen('2022_01_05', '636017782', output='data/coordinates_orpheus.csv')
csvgen('2022_01_06', '367103180', output='data/coordinates_jacksonplatte.csv')
csvgen('2022_01_15', '366973130', output='data/coordinates_malaga.csv')
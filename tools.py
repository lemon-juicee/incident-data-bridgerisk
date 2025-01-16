import numpy as np
import pandas as pd

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
def pos_angle(angle):
    """
    pos_angle() converts angles from negative degrees to positive degrees while maintaining the same magnitude and orientation, and also adjusts angles above 360 degrees to be within the range [0,360]
    Parameters:
    angle = the input angle
        type = int
    Returns:
    angle = the angle, adjusted to be positive (as low as possible)
        type = int
    """

    while angle < 0:
        angle += 360
    while angle > 360:
        angle -= 360
    return angle

def true_difference(angle1, angle2):
    """
    Creates a difference of two angles as follows:
    If 0 < true_difference < 180, then angle1 is clockwise of angle2, measured by the interior angle
    If -180 < true_difference < 0, then angle1 is counterclockwise of angle2, measured by itnerior angle
    Angles with a difference of 0, -180, or 180 are left unchanged
    It is recommended for pos_angle() to be used on both angles beforehand
    Parameters:
    angle1 = the first angle, according to the rules above
        type = int
    angle2 = the second angle, according to the rules above
        type = int
    Returns:
    diff = the difference of the angles as described above
        type = int
    """

    if angle1-angle2 > 180:
        diff = (-1)*(360 - angle1 + angle2)
    if angle1-angle2 < -180:
        diff = 360 + angle1 - angle2
    if angle1-angle2 > -180 and angle1-angle2 < 180:
        diff = angle1-angle2
    if angle1-angle2 == 180:
        diff = 180
    if angle1-angle2 == -180:
        diff = -180
    if angle1-angle2 == 0:
        diff = 0
    return diff

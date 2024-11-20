import numpy as np
import pandas as pd
from pathlib import Path
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import datetime

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

# difference_cog_heading() written by Natalia Dougan
def difference_cog_heading(df): 
    differences = []
    for row in range(df.shape[0]): 
        cog = df.loc[row,'COG']
        if cog == 360: 
            cog = 0.0
        heading = df.loc[row,'Heading']
        difference = cog - heading
        differences.append(difference)
    df['Difference in COG and Heading'] = differences
    return df

# Code from here written by Lemon Doroshow
def incident_graph(path, MMSI, time, show_angle_difference=False, show_status=False):
    """
    Parameters:
    incident_graph() shows a graph of a day's worth of AIS data for one ship
    path = The date of an AIS csv file; ex: for the file AIS_2018_12_31.csv, path = '2018_12_31' in YYYY_MM_DD format
        type = str
    MMSI = The MMSI of the ship in question
        type = str (returns an empty dataframe if MMSI is entered as an int or float)
    time = the time of the event, used to plot, vertical line on the graph
        type = string, format 'HH:MM:SS'
    show_angle_difference = Plots angle_difference graph
        type = bool
    show_status = Plots status graph
        type = bool
    Returns:
    
    """

    # Import data into a dataframe, filtering for MMSI, add angle difference
    data = Generic_Mask_Filter(("data/AIS_" + path + '.csv'), MMSI=[MMSI])
    data = difference_cog_heading(data)

    # Adjust times and dates to fit YYYY-MM-DD and HH:MM:SS
    times_raw = pd.to_datetime([strings for strings in data["BaseDateTime"]]).time
    hours = [t.hour for t in times_raw]
    minutes = [t.minute for t in times_raw]
    seconds = [t.second for t in times_raw]
    times_adjusted = [f"{h:02}:{m:02}:{s:02}" for h, m, s in zip(hours, minutes, seconds)]
    """ Unused date adjustment code
    date_raw = pd.to_datetime([strings for strings in data["BaseDateTime"]]).date
    year = date_raw[0].year # Index at 0 because each date should be the same in one day of AIS data
    month = date_raw[0].month 
    day  = date_raw[0].day
    date_adjusted=f"{year}-{month}-{day}" 
    """

    # Extract status and angle difference data  
    statuses = data['Status']
    angle_difference = data['Difference in COG and Heading']

    # Define dataframe containing times, statuses, and angle differences
    mapped_data = {'time':times_adjusted, 'status': statuses, 'angle_difference': angle_difference}
    mapped_df = pd.DataFrame(mapped_data)

    # Set up figure and axes
    fig, ax = plt.subplots()
    plt.xlabel('Time (UTC)')
    ax.xaxis.set_major_locator(ticker.LinearLocator(10))
    ax.tick_params(axis='x',labelrotation=45)

    # Display plots of chosen variable as a function of time
    if show_angle_difference and show_status:
        raise Exception("Please choose either status or angle difference!")
    elif show_status:
        ax.set_ylim(0, 15)
        ax.scatter(mapped_df['time'], mapped_df['status'])
        plt.ylabel('Status')
    elif show_angle_difference:
        ax.scatter(mapped_df['time'], mapped_df['angle_difference'])
        plt.ylabel('Angle Difference (deg)')
    
    # Create a vertical line at the time of the incident
    time = pd.to_datetime(time)
    time_hour= time.hour
    time_minute = time.minute
    time_second  = time.second
    time_final=f"{time_hour:02}:{time_minute:02}:{time_second:02}"
    plt.axvline(time_final)

incident_graph('2022_01_06', '367103180', '05:00:00', show_angle_difference=True)

#plt.title('MALAGA Loss of Propulsion - 01/15/2022')
plt.show()

"""path = '2022_01_06'

data = Generic_Mask_Filter(("data/AIS_" + path + '.csv'), MMSI=['367103180'])

# Adjust times to be a single number; import statuses; calculate aberrancies
times_adjusted = pd.to_datetime([strings[-8:] for strings in data["BaseDateTime"]], format='%H:%M:%S').time
hours = [t.hour for t in times_adjusted]
minutes = [t.minute for t in times_adjusted]
seconds = [t.second for t in times_adjusted]
time_labels = [f"{h:02}:{m:02}:{s:02}" for h, m, s in zip(hours, minutes, seconds)]

print(time_labels)"""



import numpy as np
import pandas as pd
from pathlib import Path
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import datetime
import math

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
def closest(lst, K):
    """
    closest() finds the closest value in a list to the given value
    Parameters:
    lst = the input list to search through
        type = list
    K = the value to find a list value closest to
        type = int
    Returns:
    idx = the closest value in lst to K
        type = depends on the members of lst
    """

    lst = np.asarray(lst)
    idx = (np.abs(lst - K)).argmin()
    return idx

def pos_angle(angle):
    """
    pos_angle() converts angles from negative degrees to positive degrees while maintaining the same magnitude and orientation
    Parameters:
    angle = the input angle
        type = int
    Returns:
    angle = the angle, adjusted to be positive (as low as possible)
        type = int
    """

    while angle < 0:
        angle = angle + 360
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

def incident_graph(path, MMSI, time, plot_together=False):
    """
    incident_graph() shows a graph of a day's worth of AIS data for one ship
    Parameters:
    path = The date of an AIS csv file; ex: for the file AIS_2018_12_31.csv, path = '2018_12_31' in YYYY_MM_DD format
        type = str
    MMSI = The MMSI of the ship in question
        type = str (returns an empty dataframe if MMSI is entered as an int or float)
    time = the time of the event, used to plot, vertical line on the graph
        type = string, format 'HH:MM:SS'
    plot_togeter = Whether to plot the lat-lon colormap and the statuses as well as the angle difference, False by default
        type = Boolean
    Returns:
    matplotlib figure to be called with plt.show() or plt.savefig()
    """

    # Import data into a dataframe, filtering for MMSI; removing Heading = 511.0 and adjusting COG according to https://coast.noaa.gov/data/marinecadastre/ais/faq.pdf
    data = Generic_Mask_Filter(("data/AIS_" + path + '.csv'), MMSI=[MMSI])
    data_511 = data[(data['Heading'] == 511.0) | (data['COG'] == 360.0)]
    data = data[(data['Heading'] != 511.0) & (data['COG'] != 360.0)]
    data['COG'] = [cog + 409.6 if cog < 0 else cog for cog in data['COG']]

    # Adjust times and dates to fit YYYY-MM-DD and HH:MM:SS
    times_raw = pd.to_datetime([strings for strings in data["BaseDateTime"]]).time
    hours = [t.hour for t in times_raw]
    minutes = [t.minute for t in times_raw]
    seconds = [t.second for t in times_raw]
    times_adjusted = [h + m/60 + s/3600 for h, m, s in zip(hours, minutes, seconds)]
    times_raw_511 = pd.to_datetime([strings for strings in data_511["BaseDateTime"]]).time
    hours_511 = [t.hour for t in times_raw_511]
    minutes_511 = [t.minute for t in times_raw_511]
    seconds_511 = [t.second for t in times_raw_511]
    times_adjusted_511 = [h + m/60 + s/3600 for h, m, s in zip(hours_511, minutes_511, seconds_511)]
    
    # Adjust incident time to fit HH:MM:SS
    time = pd.to_datetime(time)
    time_hour= time.hour
    time_minute = time.minute
    time_second  = time.second
    time_final = time_hour + time_minute/60 + time_second/3600

    # Extract status and angle difference data  
    statuses = data['Status']
    angle_difference = [true_difference(pos_angle(cog), pos_angle(heading)) for cog, heading in zip(data['COG'], data['Heading'].astype(np.float64))]

    # Define dataframe containing times, statuses, and angle differences
    mapped_data = {'time':times_adjusted, 'status': statuses, 'angle_difference':angle_difference, 'true_times':[a.hour+a.minute/60 for a in times_raw]}
    mapped_data_511 = {'time':times_adjusted_511, 'angle_difference':[0] * len(data_511['Heading'].tolist())}
    mapped_df = pd.DataFrame(mapped_data)
    mapped_df_511 = pd.DataFrame(mapped_data_511)

    # Set up figure and axes
    if plot_together:
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(12,4))
    else:
        fig, ax = plt.subplots()
    
    # Labelling status and angle difference graphs
    if plot_together:
        ax1.xaxis.set_major_locator(ticker.LinearLocator(8))
        ax1.tick_params(axis='x',labelrotation=45)
        ax1.set_xlabel('Time (UTC)')
        ax1.set_ylabel('Status')
        ax2.xaxis.set_major_locator(ticker.LinearLocator(8))
        ax2.tick_params(axis='x',labelrotation=45)
        ax2.set_xlabel('Time (UTC)')
        ax2.set_ylabel('Angle Difference (deg)')
        ax3.set_xlabel('Latitude (deg)')
        ax3.set_ylabel('Longitude(deg)')
    else:
        ax.xaxis.set_major_locator(ticker.LinearLocator(8))
        ax.tick_params(axis='x',labelrotation=45)
        ax.set_xlabel('Time (UTC)')
        ax.set_ylabel('Angle Difference (deg)')

    # Create scatter plots with vertical line at incident time
    if plot_together:
        ax1.scatter(mapped_df['time'], mapped_df['status'])
        ax2.scatter(mapped_df['time'], mapped_df['angle_difference'])
        ax2.scatter(mapped_df_511['time'], mapped_df_511['angle_difference'], color='red')
        ax1.axvline(time_final)
        ax2.axvline(time_final)
    else:
        ax.scatter(mapped_df['time'], mapped_df['angle_difference'])
        ax.scatter(mapped_df_511['time'], mapped_df_511['angle_difference'], color='red')
        ax.axvline(time_final)
        fig.tight_layout()

    if plot_together:
        # Set up incident time for color map
        color = mapped_df['true_times']
        incident_time = time_hour+time_minute/60
        inc_loc = closest(color, incident_time)
    
        # Create lat-long map with colorbar and point where incident occurs
        plot = ax3.scatter(data['LAT'],data['LON'], c=color)
        dot = ax3.plot(data['LAT'].tolist()[inc_loc], data['LON'].tolist()[inc_loc], 'vk', markersize='10', fillstyle='none')
        cbar = fig.colorbar(plot)

        # Add space between plots
        plt.subplots_adjust(wspace=0.5, hspace=0.5)

def stddev_anglemap(path, MMSI):
    """
    stddev_anglemap() creates a histogram of a ship's angle differences over the course of a day
    Parameters:
    path = The date of an AIS csv file; ex: for the file AIS_2018_12_31.csv, path = '2018_12_31' in YYYY_MM_DD format
        type = str
    MMSI = The MMSI of the ship in question
        type = str (returns an empty dataframe if MMSI is entered as an int or float)
    Returns:
    matplotlib figure to be called with plt.show() or plt.savefig()
    """

    # Import data from csv and filter out null heading values
    data = Generic_Mask_Filter(("data/AIS_" + path + '.csv'), MMSI=[MMSI])
    data = data[(data['Heading'] != 511.0) & (data['COG'] != 360.0)]

    # Calculate angle difference
    angle_difference = [true_difference(pos_angle(cog), pos_angle(heading)) for cog, heading in zip(data['COG'], data['Heading'].astype(np.float64))]
    
    # Plot frequency histogram (as denoted by weights) with 25 bins
    plt.hist(angle_difference, bins=25, weights=np.ones_like(angle_difference) / np.size(angle_difference))

def change_graph(path, MMSI, time, measurement):
    """
    change_graph() shows a plot of the change in a certain variable of a ship's movement at each broadcast point
    Parameters:
    path = The date of an AIS csv file; ex: for the file AIS_2018_12_31.csv, path = '2018_12_31' in YYYY_MM_DD format
        type = str
    MMSI = The MMSI of the ship in question
        type = str (returns an empty dataframe if MMSI is entered as an int or float)
    time = the time of the event, used to plot, vertical line on the graph
        type = string, format 'HH:MM:SS'
    measurement = which variable to plot the change of
        type = string, either 'COG', 'Heading', or 'Difference' (case sensitive)
    Returns:
    matplotlib figure to be called with plt.show() or plt.savefig()
    """

    # Import AIS data
    data = Generic_Mask_Filter(("data/AIS_" + path + '.csv'), MMSI=[MMSI])

    # Adjust AIS data times
    times_raw = pd.to_datetime([strings for strings in data["BaseDateTime"]]).time
    hours = [t.hour for t in times_raw]
    minutes = [t.minute for t in times_raw]
    seconds = [t.second for t in times_raw]
    times_adjusted = [h + m/60 + s/3600 for h, m, s in zip(hours, minutes, seconds)]

    # Adjust incident time
    time = pd.to_datetime(time)
    time_hour= time.hour
    time_minute = time.minute
    time_second  = time.second
    time_final = time_hour + time_minute/60 + time_second/3600

    # Set up subplots
    fig, ax = plt.subplots()

    # Format axes
    ax.xaxis.set_major_locator(ticker.LinearLocator(8))
    ax.tick_params(axis='x',labelrotation=45)
    ax.set_xlabel('Time (UTC)')

    # Heading DF construction
    if measurement == "Heading":

        # Remove null values and create sorted DF
        data = data[data['Heading'] != 511.0]
        mapped_data = {'time':times_adjusted, 'Heading':data['Heading']}
        mapped_df = pd.DataFrame(mapped_data)
        mapped_df = mapped_df.sort_values('time')
        headings = mapped_df['Heading'].tolist()

        # Create a new dataframe with the change in heading calculated at each point - the initial point is equal to zero
        change = [0]
        i = 1
        while i < len(headings):
            change.append(headings[i] - headings[i-1])
            i += 1
        mapped_data = {'time':times_adjusted, 'change':change}
        mapped_df = pd.DataFrame(mapped_data)
        ax.set_ylabel('Change in Heading (deg)')

    # COG DF construction
    elif measurement == 'COG':

        # Create sorted DF
        data = data[data['COG'] != 360.0]
        mapped_data = {'time':times_adjusted, 'COG':data['COG']}
        mapped_df = pd.DataFrame(mapped_data)
        mapped_df = mapped_df.sort_values('time')
        cogs = mapped_df['COG'].tolist()

        # Create a new dataframe with the change in COG calculated at each point - initial is equal to zero
        change = [0]
        i = 1
        while i < len(cogs):
            change.append(cogs[i] - cogs[i-1])
            i += 1
        mapped_data = {'time':times_adjusted, 'change':change}
        mapped_df = pd.DataFrame(mapped_data)
        ax.set_ylabel('Change in COG (deg)')

    # Angle difference DF construction
    elif measurement == 'Difference':

        # Calculate angle differences and create sorted dataframe
        data = data[(data['Heading'] != 511.0) & (data['COG'] != 360.0)]
        angle_difference = [true_difference(pos_angle(cog), pos_angle(heading)) for cog, heading in zip(data['COG'], data['Heading'].astype(np.float64))]
        mapped_data = {'time':times_adjusted, 'difference':angle_difference}
        mapped_df = pd.DataFrame(mapped_data)
        mapped_df = mapped_df.sort_values('time')
        diffs = mapped_df['difference'].tolist()

        # Create new dataframe with the change in angle difference at each point - initial is equal to zero
        change = [0]
        i = 1
        while i < len(diffs):
            change.append(diffs[i] - diffs[i-1])
            i += 1
        mapped_data = {'time':times_adjusted, 'change':change}
        mapped_df = pd.DataFrame(mapped_data)
        ax.set_ylabel('Change in Angle Difference (deg)')

    # Raise an exception if the measurements argument is formatted incorrectly
    else:
        raise Exception("Please choose COG, Heading, or Difference! (case sensitive)")
    
    # Plot scatterplot of chosen changes along with a vertical line at the time of incident
    ax.scatter(mapped_df['time'], mapped_df['change'])
    ax.axvline(time_final)
"""
incident_graph('2019_01_08', '366995430', '02:20:00')
plt.title('ZEUS, Allision - 01/08/2019')
plt.savefig('graphics/ZEUS, Allision.png', bbox_inches='tight')
plt.clf()

incident_graph('2019_01_24', '366998110', '19:30:00')
plt.title('STEVE RICHOUX, Allision - 01/24/2019')
plt.savefig('graphics/STEVE RICHOUX, Allision.png', bbox_inches='tight')
plt.clf()

incident_graph('2019_02_17', '367638130', '20:25:00')
plt.title('JOSEPH PATRICK ECKSTEIN, Allision - 02/17/2019')
plt.savefig('graphics/JOSEPH PATRICK ECKSTEIN, Allision.png', bbox_inches='tight')
plt.clf()

incident_graph('2019_02_12', '367641610', '16:15:00')
plt.title('PAUL MCGINNESS, Allision - 02/12/2019')
plt.savefig('graphics/PAUL MCGINNESS, Allision.png', bbox_inches='tight')
plt.clf()

incident_graph('2021_03_01', '367690990', '21:15:00')
plt.title('ANGELIA B, Allision - 03/01/2021')
plt.savefig('graphics/ANGELIA B, Allision.png', bbox_inches='tight')
plt.clf()

incident_graph('2021_04_10', '338257000', '22:43:00')
plt.title('BROOKS MCCALL, Allision - 04/10/2021')
plt.savefig('graphics/BROOKS MCCALL, Allision.png', bbox_inches='tight')
plt.clf()

incident_graph('2021_06_10', '367781550', '18:05:00')
plt.title('GARLAND GASPARD, Allision - 06/10/2021')
plt.savefig('graphics/GARLAND GASPARD, Allision.png', bbox_inches='tight')
plt.clf()

incident_graph('2021_08_17', '368142750', '01:18:00')
plt.title('NYQUIST, Allision - 08/17/2021')
plt.savefig('graphics/NYQUIST, Allision.png', bbox_inches='tight')
plt.clf()

incident_graph('2022_01_24', '366946840', '00:20:00')
plt.title('MEAGHAN MARIE, Allision - 01/24/2022')
plt.savefig('graphics/MEAGHAN MARIE, Allision.png', bbox_inches='tight')
plt.clf()

incident_graph('2023_01_04', '368217370', '23:30:00')
plt.title('MISS TERRI, Allision - 01/04/2023')
plt.savefig('graphics/MISS TERRI, Allision.png', bbox_inches='tight')
plt.clf()
"""
incident_graph('2023_02_04', '367656820', '01:07:00')
plt.title('BRIANNA ELIZABETH, Allision - 02/03/2023')
plt.savefig('graphics/BRIANNA ELIZABETH, Allision.png', bbox_inches='tight')
plt.clf()

incident_graph('2023_03_22', '368236120', '04:10:00')
plt.title('JAMES E JACKSON, Allision - 03/21/2023')
plt.savefig('graphics/JAMES E JACKSON, Allision.png', bbox_inches='tight')
plt.clf()
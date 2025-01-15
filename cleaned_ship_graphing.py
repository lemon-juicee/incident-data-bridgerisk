import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from gmc import Generic_Mask_Filter

# Code written by Lemon Doroshow
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

def incident_graph(path, MMSI):
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

    # Extract status and angle difference data  
    statuses = data['Status']
    angle_difference = [true_difference(pos_angle(cog), pos_angle(heading)) for cog, heading in zip(data['COG'], data['Heading'].astype(np.float64))]

    # Define dataframe containing times, statuses, and angle differences
    mapped_data = {'time':times_adjusted, 'status': statuses, 'angle_difference':angle_difference, 'true_times':[a.hour+a.minute/60 for a in times_raw]}
    mapped_data_511 = {'time':times_adjusted_511, 'angle_difference':[0] * len(data_511['Heading'].tolist())}
    mapped_df = pd.DataFrame(mapped_data)
    mapped_df_511 = pd.DataFrame(mapped_data_511)

    # Set up figure and axes
    fig, ax = plt.subplots()
    
    # Labelling status and angle difference graphs
    ax.xaxis.set_major_locator(ticker.LinearLocator(8))
    ax.tick_params(axis='x',labelrotation=45)
    ax.set_xlabel('Time (UTC)')
    ax.set_ylabel('Angle Difference (deg)')

    # Create scatter plots with vertical line at incident time
    ax.scatter(mapped_df['time'], mapped_df['angle_difference'])
    ax.scatter(mapped_df_511['time'], mapped_df_511['angle_difference'], color='red')
    fig.tight_layout()

def change_graph(path, MMSI, measurement):
    """
    change_graph() shows a plot of the change in a certain variable of a ship's movement at each broadcast point
    Parameters:
    path = The date of an AIS csv file; ex: for the file AIS_2018_12_31.csv, path = '2018_12_31' in YYYY_MM_DD format
        type = str
    MMSI = The MMSI of the ship in question
        type = str (returns an empty dataframe if MMSI is entered as an int or float)
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

def param_hist(path, MMSI, param, change=False, kde=True):
    """
    param_hist() creates a histogram of a ship's given parameter (or change in that parameter at every AIS broadcast point) over the course of a day
    Parameters:
    path = The date of an AIS csv file; ex: for the file AIS_2018_12_31.csv, path = '2018_12_31' in YYYY_MM_DD format
        type = str
    MMSI = The MMSI of the ship in question
        type = str (returns an empty dataframe if MMSI is entered as an int or float)
    param = the parameter to collect, must be in ["LAT", "LON", "SOG", "Heading", "COG", "IMO", "Status", "Draft", "Angle Difference"]
        type = str
    change = if True, calculates the change between datapoint with index i and datapoint with index i-1 for a parameter at each AIS point
        type = bool
    kde = if True, plots a kernel density estimate along with the histogram
        type = bool
    Returns:
    matplotlib figure to be called with plt.show() or plt.savefig()
    """

    # Import data and filter
    data = Generic_Mask_Filter('data/AIS_' + path + '.csv', MMSI = [MMSI])
    if param == 'COG':
        data = data[data['COG'] != 360.0]
        data['COG'] = [cog + 409.6 if cog < 0 else cog for cog in data['COG']]
    elif param == 'Heading':
        data = data[data['Heading'] != 511.0]
    elif param == 'Angle Difference':
        data = data[(data['Heading'] != 511.0) & (data['COG'] != 360.0)]
        data['COG'] = [cog + 409.6 if cog < 0 else cog for cog in data['COG']]
    elif param == "SOG":
        data = data[data['SOG'] < 102.3]
        data['SOG'] = [sog + 102.4 if sog < 0 else sog for sog in data['SOG']]
    else: 
        pass
    data = data.sort_values(by='BaseDateTime')
    data.reset_index(drop=True, inplace=True)

    # Collect data in list depending on parameter and whether or not change = True
    if change:
        if param == 'Angle Difference':
            precol = [true_difference(pos_angle(cog), pos_angle(Heading)) for cog, Heading in zip(data['COG'].tolist(), data['Heading'].tolist())]
        else:
            precol = data[param].tolist()
        collection = [0]
        i = 1
        while i < len(precol):
            collection.append(precol[i] - precol[i-1])
            i += 1
    else:
        if param == 'Angle Difference':
            collection = [true_difference(pos_angle(cog), pos_angle(Heading)) for cog, Heading in zip(data['COG'].tolist(), data['Heading'].tolist())]
        else:
            collection = data[param].tolist()
    
    # Plot the histogram and kde, if applicable
    sns.histplot(x=collection, stat='density', bins = int(len(collection) / 10), color="royalblue")
    if kde:    
        sns.kdeplot(x=collection, color='black')

    
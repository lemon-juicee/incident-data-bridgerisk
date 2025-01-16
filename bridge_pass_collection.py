import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from geopy import distance
from tools import Generic_Mask_Filter, pos_angle, true_difference

# Code written by Lemon Doroshow
def bridge_reader(path):
    """
    bridge_reader() imports a pre-made csv including all of the AIS data points before and after a ship passes under a ship
    Parameters:
    path = the bridge csv file's path - MUST BE a csv file pre-compiled from our GitHub repo
        type = str
    Returns
    passes_paired = pandas dataframe containing the MMSI, date, and times before and after each pass
        type = pandas.DataFrame
    """

    # Import csv
    df = pd.read_csv(path, sep=',', header=0, on_bad_lines="skip")

    # Remove duplicated heading rows
    df = df[df['MMSI'] != 'MMSI']
    df.reset_index(drop=True, inplace=True)

    # Define dataframe objects for before and after each pass
    passes = pd.DataFrame({'MMSI':df['MMSI'], 'BaseDateTime':df['BaseDateTime'], 'Width':df['Width']})
    initials = passes[passes.index % 2 == 0]
    finals = passes[passes.index % 2 == 1]

    # Pair the data for each pass into a single dataframe object
    passes_paired = pd.DataFrame({'MMSI':[], 'date':[], 'time_before':[], 'time_after':[], 'Width':[]})
    for i, f in zip(initials.itertuples(), finals.itertuples()):
        if i.BaseDateTime[:10] != f.BaseDateTime[:10]: # Since we base the date off of our initial pass,
            raise Exception("The ship passed under a bridge at midnight!") # we would want to know if the initial and final pass aren't on the same day
        pairing = {'MMSI':i.MMSI, 'date':i.BaseDateTime[:10].replace('-','_'), 'time_before':i.BaseDateTime, 'time_after':f.BaseDateTime, 'Width':i.Width}
        passes_paired.loc[len(passes_paired)] = pairing
    
    return passes_paired

def param_collection(path, param, large=False):
    """
    param_collection() takes a csv file (formatted the same way as bridge_reader()'s input) and collects a certain parameter for every bridge pass in the file and ~5 miles up and downstream
    Parameters:
    path = the bridge csv file's path - MUST BE a csv file pre-compiled from our GitHub repo
        type = str
    param = the parameter to collect, must be in ["LAT", "LON", "SOG", "Heading", "COG", "IMO", "Status", "Draft", "Angle Difference"]
        type = str 
    Returns:
    collection = the collection of the parameters in the ~10 mile range up and downstream from the bridge pass
        type = list
    """
    # Build bridge dataframe 
    bridge_df = bridge_reader(path)
    if large:
        bridge_df = bridge_df[bridge_df['Width'].notna()]
        bridge_df['Width'] = bridge_df['Width'].astype(int)
        bridge_df = bridge_df[bridge_df['Width'] >= 150]
    collection = []

    for passing in bridge_df.itertuples(): # Iterates through the dataframe by row (for each pass)

        # Import data by pass and filter depending on parameter
        data = Generic_Mask_Filter('data/AIS_' + passing.date + '.csv', MMSI = [str(passing.MMSI)])
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

        # Upstream loop
        ind = 0 # For debugging
        index_before = data.index[data['BaseDateTime'] == passing.time_before][0]
        distance_before = 0
        coordinate_prior = (data['LAT'].tolist()[index_before], data['LON'].tolist()[index_before])

        while distance_before <= 5: # 5 miles upstream
            # Coordinate variables used to measure the distance between each datapoint as we iterate
            coordinate = (data['LAT'].tolist()[index_before], data['LON'].tolist()[index_before])
            coordinate_prior = (data['LAT'].tolist()[index_before + 1], data['LON'].tolist()[index_before + 1])
            if param != 'Angle Difference':
                collection.append(data[param].tolist()[index_before])
            elif param == 'Angle Difference':
                # Calculates angle difference according to rules set out in true_difference() function definition
                anglediff = true_difference(pos_angle(data['COG'].tolist()[index_before]), pos_angle(data['Heading'].tolist()[index_before]))
                collection.append(anglediff)
            distance_before += distance.distance(coordinate, coordinate_prior).miles # Uses geopy's distance library to find the distance in miles between datapoints and add it to cumulative 
            print('For index' + str(index_before) + ' on ship' + str(passing.MMSI) + " at time " + data['BaseDateTime'].tolist()[index_before]) # For debugging
            print("The added " + param + " is " + str(collection[ind])) # For debugging
            print("And the cumulative distance is " + str(distance_before) + "\n") # For debugging
            index_before -= 1 # Index decreases since we are moving "back in time"
            ind += 1 # For debugging

        # Downstream loop
        index_after = data.index[data['BaseDateTime'] == passing.time_after][0]
        distance_after = 0
        coordinate_prior = (data['LAT'].tolist()[index_after], data['LON'].tolist()[index_after])

        while distance_after <= 5: # 5 miles downstream 
            coordinate = (data['LAT'].tolist()[index_after], data['LON'].tolist()[index_after])
            coordinate_prior = (data['LAT'].tolist()[index_after - 1], data['LON'].tolist()[index_after - 1])
            if param != 'Angle Difference':    
                collection.append(data['COG'].tolist()[index_after])
            elif param == 'Angle Difference':
                # Calculates angle difference according to rules set out in true_difference() function definition
                anglediff = true_difference(pos_angle(data['COG'].tolist()[index_after]), pos_angle(data['Heading'].tolist()[index_after]))
                collection.append(anglediff)
            distance_after += distance.distance(coordinate, coordinate_prior).miles # Uses geopy's distance library to find the distance in miles between datapoints and add it to cumulative 
            print('For index ' + str(index_after) + ' on ship ' + str(passing.MMSI) + " at time " + data['BaseDateTime'].tolist()[index_after]) # For debugging
            print("The added " + param + " is " + str(collection[ind])) # For debugging
            print("And the cumulative distance is " + str(distance_after) + "\n") # For debugging
            index_after += 1 # Index increases since we are now moving forward in time
            ind += 1 # For debugging

        print(str(passing.Index + 1) + "/" + str(len(bridge_df)) + " through the pass data.") # For debugging
    
    return collection

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from geopy import distance
from gmc import Generic_Mask_Filter

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
    passes = pd.DataFrame({'MMSI':df['MMSI'], 'BaseDateTime':df['BaseDateTime']})
    initials = passes[passes.index % 2 == 0]
    finals = passes[passes.index % 2 == 1]

    # Pair the data for each pass into a single dataframe object
    passes_paired = pd.DataFrame({'MMSI':[], 'date':[], 'time_before':[], 'time_after':[]})
    for i, f in zip(initials.itertuples(), finals.itertuples()):
        if i.BaseDateTime[:10] != f.BaseDateTime[:10]: # Since we base the date off of our initial pass,
            raise Exception("The ship passed under a bridge at midnight!") # we would want to know if the initial and final pass aren't on the same day
        pairing = {'MMSI':i.MMSI, 'date':i.BaseDateTime[:10].replace('-','_'), 'time_before':i.BaseDateTime, 'time_after':f.BaseDateTime}
        passes_paired.loc[len(passes_paired)] = pairing
    
    return passes_paired

def param_collection(path, param):
    # WiP docstring: the goal of param_collection() is to take a dataframe compiled by bridge_reader() 
    # and collect the COGs 5 miles upstream and downstream from the time of pass
    if param in ["LAT", "LON", "SOG", "Heading", "COG", "IMO", "Status", "Draft", "Angle Difference"]:
        pass
    else:
        raise Exception('Please choose a parameter within the AIS data, or "Angle Difference"')
    bridge_df = bridge_reader(path)
    collection = []
    for passing in bridge_df.itertuples():
        data = Generic_Mask_Filter('data/AIS_' + passing.date + '.csv', MMSI = [str(passing.MMSI)])
        data = data.sort_values(by='BaseDateTime')
        data.reset_index(drop=True, inplace=True)

        index_before = data.index[data['BaseDateTime'] == passing.time_before][0]
        distance_before = 0
        coordinate_prior = (data['LAT'].tolist()[index_before], data['LON'].tolist()[index_before])
        while distance_before <= 5:
            coordinate = (data['LAT'].tolist()[index_before], data['LON'].tolist()[index_before])
            coordinate_prior = (data['LAT'].tolist()[index_before + 1], data['LON'].tolist()[index_before + 1])
            if param != 'Angle Difference':
                collection.append(data[param].tolist()[index_before])
            distance_before = distance_before + distance.distance(coordinate, coordinate_prior).miles
            print('For index' + str(index_before) + ' on ship' + str(passing.MMSI)) # For debugging
            print("The added" + param + " is " + str(data['COG'].tolist()[index_before])) # For debugging
            print("And the cumulative distance is " + str(distance_before) + "\n") # For debugging
            index_before -= 1

        index_after = data.index[data['BaseDateTime'] == passing.time_after][0]
        distance_after = 0
        coordinate_prior = (data['LAT'].tolist()[index_after], data['LON'].tolist()[index_after])
        while distance_after <= 5:
            coordinate = (data['LAT'].tolist()[index_after], data['LON'].tolist()[index_after])
            coordinate_prior = (data['LAT'].tolist()[index_after - 1], data['LON'].tolist()[index_after - 1])
            if param != 'Angle Difference':    
                collection.append(data['COG'].tolist()[index_after])
            distance_after = distance_after + distance.distance(coordinate, coordinate_prior).miles
            print('For index ' + str(index_after) + ' on ship ' + str(passing.MMSI)) # For debugging
            print("The added" + param + " is " + str(data['COG'].tolist()[index_after])) # For debugging
            print("And the cumulative distance is " + str(distance_after) + "\n") # For debugging
            index_after += 1
    
    return collection

cogs = param_collection('data/testbridge.csv', 'COG')
print(cogs)
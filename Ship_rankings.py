## Written by Natalia Dougan
## Edited by Diran Jimenez

 import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import os
import textwrap
from matplotlib.backends.backend_pdf import PdfPages

# This file path should link to the data on your machine
folder_path = r"C:\Users\natal\OneDrive\Desktop\Key_bridge_filter_plot\Bridge Result Data\Filtered Data"

# Dictionary to store average ships per day for each bridge with no size requirement
bridge_results = {}

# Process each CSV file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        
        df = pd.read_csv(file_path, header=None)

        # Drops all the rows with headers and re-adds just one row of headers to the columns
        df_no_header = df[df[0] != 'MMSI']
        df_no_header.columns = ['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG', 'COG', 'Heading', 'VesselName', 'IMO', 'CallSign', 'VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass']
        
        df_no_header = df_no_header.copy()
        # Since each trip has two rows of data, take the length of the df and divide by 2
        num_trips = ((df_no_header.shape[0])/2)
        
        # Find the average daily trips
        daily_trips = num_trips / (2282) # This is the number of days of data that have been processed
            # See the length of URLs in Advanced AIS Filtering
            
        # Save the data
        bridge_results[filename] = [daily_trips, num_trips]


# Takes the "csv" and "Data" out of the filename so it can be used as a bridge name
bridge_results = {name.replace('.csv', '').replace(' Data', '').replace('BRIDGE',''): value for name, value in bridge_results.items()}


# Sort results from largest to smallest
filtered_Bridge_results = dict(sorted(bridge_results.items(), key=lambda item: item[1][0], reverse=True))

# Store all the sorted results into a dataframe
Bridge_results_df = pd.DataFrame([{"Bridge": i, "Daily Trips": j[0], "Total Trips": j[1]}  for i, j in filtered_Bridge_results.items()])

# Saves the results to a csv 
Bridge_results_df.to_csv(r"C:\Users\natal\OneDrive\Desktop\Key_bridge_filter_plot\Rankings New\Trip Data for all Large Ships.csv", index=False)

# Focus on bridges that have more than 1 trip per day on average
filtered_results = {k: v[0] for k, v in filtered_Bridge_results.items() if v[0] >= 1}
bridges_with_traffic = [(i, j) for i, j in filtered_results.items()]


# These bridges are of particular note based on group discussion and will be highlighted
#important_bridges = ["SUNSHINE SKYWAY BRIDGE", "CHESAPEAKE BAY BRIDGE", "FRANCIS SCOTT KEY BRIDGE", "VERZZANO NARROWS BRIDGE"]
    # If more bridges become relavent, add them to this list and remake the graphs

def wrap_labels(labels, width=10):
    return ['\n'.join(textwrap.wrap(label,width)) for label in labels]
    
# Make a figure for the top 10, 25, and 50 bridges
for n in [10, 25, 50]:
    plt.figure(figsize=(20, 8))
    
    if n == 10:
        wrapped_labels = wrap_labels([b[0] for b in bridges_with_traffic[:n]], width=18)
        plt.xticks(range(len(wrapped_labels)), wrapped_labels, ha='center', font='Verdana', fontsize=10)
        plt.xlabel('Bridge Names', font='Verdana', fontsize =16)
        plt.ylabel('Average Ships per Day', font='Verdana', fontsize =16)
        plt.title(f'Top {n} Busiest Bridges', font='Verdana', fontsize =20)
        
        # Make a bar plot with the exact traffic labeled at the top of each bar
        for b in bridges_with_traffic[:n]:
            plt.bar(b[0], b[1], color='#87CEEB')
            plt.text(b[0], b[1], f'{b[1]:.2f}', ha='center', va='bottom', font='Verdana', fontsize=12)
    elif n == 25: 
        wrapped_labels = wrap_labels([b[0] for b in bridges_with_traffic[:n]], width=20)
        plt.xticks(range(len(wrapped_labels)), wrapped_labels, rotation = 45, font='Verdana', ha='right', fontsize=10)
        plt.xlabel('Bridge Names', font='Verdana', fontsize =14)
        plt.ylabel('Average Ships per Day', font='Verdana', fontsize =14)
        plt.title(f'Top {n} Busiest Bridges', font='Verdana', fontsize =16)
        
        # Make a bar plot with the exact traffic labeled at the top of each bar
        for b in bridges_with_traffic[:n]:
            plt.bar(b[0], b[1], color='#87CEEB')
            plt.text(b[0], b[1], f'{b[1]:.2f}', ha='center', va='bottom', font='Verdana', fontsize=10)
    else: 
        plt.xticks(rotation=45, ha='right', font='Verdana', fontsize=10)
        plt.xlabel('Bridge Names', font='Verdana', fontsize =12)
        plt.ylabel('Average Ships per Day', font='Verdana', fontsize =12)
        plt.title(f'Top {n} Busiest Bridges', font='Verdana', fontsize =14)
        
        # Make a bar plot with the exact traffic labeled at the top of each bar
        for b in bridges_with_traffic[:n]:
            plt.bar(b[0], b[1], color='#87CEEB')
            plt.text(b[0], b[1], f'{b[1]:.2f}', ha='center', va='bottom', font='Verdana', fontsize=8)


    plt.tight_layout()
    plt.grid(axis='y', linestyle=':', color='gray', alpha=0.5, zorder=0)  
         
        
        # If you need a written list of the rankings, uncomment this section
        # if n == 50:
        #     i = 0
        #     print()
        #     print("Ranking with All Large Ships")
        #     for b in bridges_with_traffic[:50]:
        #         i += 1
        #         print(f"{i}: {b[0]} - {b[1]:.4f} Average Daily Trips")
    plot_file_path = r"C:\Users\natal\OneDrive\Desktop\Key_bridge_filter_plot\Rankings New\Top "+str(n)+" Busiest Bridges.pdf"
    plt.savefig(plot_file_path)
    plt.close()
        
print("Busiest Bridges PDFs saved")


# These lengths have been arbitrarily chosen as cutoffs for different sizes of ship
length_thresholds = [180, 215, 250, 275, 300]
       

# Saving the data into a dictionary of dictionaries
all_bridge_results = {threshold: {} for threshold in length_thresholds}

def process_data_for_threshold(threshold):
    bridge_results = {}
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            
            df = pd.read_csv(file_path, header=None)
            
            
            df_no_header = df[df[0] != 'MMSI']
            df_no_header.columns = ['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG', 'COG', 'Heading', 'VesselName', 'IMO', 'CallSign', 'VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass']
            
            df_no_header = df_no_header.copy()
            
            
            df_filtered = df_no_header[df_no_header['Length'].astype(float) > threshold]
            
            df_filtered = df_filtered.copy()
            
            num_trips = ((df_filtered.shape[0])/2)
            daily_trips = num_trips / (2282)
            
            bridge_results[filename] = [daily_trips, num_trips]
    
    # Clean up bridge names
    bridge_results = {name.replace('.csv', '').replace(' Data', '').replace('BRIDGE',''): value for name, value in bridge_results.items()}
    
    return bridge_results

for threshold in length_thresholds:
    # add data dictionary for threshold to i index of dictionary
    all_bridge_results[threshold] = process_data_for_threshold(threshold)
    
    filtered_Bridge_results = dict(sorted(all_bridge_results[threshold].items(), key=lambda item: item[1], reverse=True))
    
    # Create DataFrame from results
    Bridge_results_df = pd.DataFrame([{"Bridge": i, "Daily Trips": j[0], "Total Trips": j[1]}  for i, j in filtered_Bridge_results.items()])
    
    # Optionally save to CSV
    Bridge_results_df.to_csv(rf"C:\Users\natal\OneDrive\Desktop\Key_bridge_filter_plot\Rankings New\Trip Data for Ships Longer than {threshold} meters.csv", index=False)
    
    # Filter on bridges with traffic above 0.1 trips per day, on average
    filtered_results = {k: v[0] for k, v in filtered_Bridge_results.items() if v[0] >= 0.1}
        # With larger ship sizes, traffic significantly decreases
    
    traffic = [(i, j) for i, j in filtered_results.items()]
    
    
    for n in [10, 15, min(n, len(traffic))]:
            
        plt.figure(figsize=(20, 8))

        if n <= 10:
            wrapped_labels = wrap_labels([b[0] for b in traffic[:n]], width=18)
            plt.xticks(range(len(wrapped_labels)), wrapped_labels, ha='center', font='Verdana', fontsize=10)
            plt.xlabel('Bridge Names', font='Verdana', fontsize =16)
            plt.ylabel('Average Ships per Day', font='Verdana', fontsize =16)
            plt.title(f'Top {min(n, len(traffic))} Busiest Bridges with Ship Lengths above {threshold} meters', fontsize =20)
                
            for b in traffic[:n]:
                plt.bar(b[0], b[1], color='#87CEEB')
                plt.text(b[0], b[1], f"{b[1]:.2f}", ha='center', va='bottom', font='Verdana', fontsize=12)
        elif n <= 25: 
            wrapped_labels = wrap_labels([b[0] for b in traffic[:n]], width=20)
            bar_positions = np.arange(n)
            plt.bar(bar_positions, [b[1] for b in traffic[:n]], color='#87CEEB')
            plt.xticks(bar_positions, wrapped_labels, rotation=45, ha='right', font='Verdana', fontsize=10)
            plt.xlabel('Bridge Names', font='Verdana', fontsize =14)
            plt.ylabel('Average Ships per Day', font='Verdana', fontsize =14)
            plt.title(f'Top {min(n, len(traffic))} Busiest Bridges with Ship Lengths above {threshold} meters', fontsize =16)
                
            for b in traffic[:n]:
                plt.bar(b[0], b[1], color='#87CEEB')
                plt.text(b[0], b[1], f"{b[1]:.2f}", ha='center', va='bottom', font='Verdana', fontsize=10)
        else: 
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.xlabel('Bridge Names', font='Verdana', fontsize =12)
            plt.ylabel('Average Ships per Day', font='Verdana', fontsize =12)
            plt.title(f'Top {min(n, len(traffic))} Busiest Bridges with Ship Lengths above {threshold} meters', fontsize =14)
                
            for b in traffic[:n]:
                plt.bar(b[0], b[1], color='#87CEEB')
                plt.text(b[0], b[1], f"{b[1]:.2f}", ha='center', va='bottom', font='Verdana', fontsize=8)
                
        plt.tight_layout()
        plt.grid(axis='y', linestyle=':', color='gray', alpha=0.5, zorder=0)  
        
        plot_file_path = r"C:\Users\natal\OneDrive\Desktop\Key_bridge_filter_plot\Rankings New\Top "+str(n)+f" Busiest Bridges with Ship Lengths Above {threshold} meters.pdf"
        plt.savefig(plot_file_path, format='pdf')
        plt.close()
            
            # if n == 50:
            #     i = 0
            #     print()
            #     print(f"Ranking with Ships Larger than {threshold} m:")
            #     for b in traffic[:50]:
            #         i += 1
            #         print(f"{i}. {b[0]} - {b[1]:.4f} Average Daily Trips")
                    
    print(f"Plot saved to {plot_file_path}.pdf saved") 
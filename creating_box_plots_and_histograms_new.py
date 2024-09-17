## Written by Diran Jimenez
## Updated by Natalia 9/06/2024

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns



# Get the list of bridges from our GitHub
bridge_data = pd.read_excel("Corrected_Bridge_Boundaries.xlsx", header=0, index_col = 0, usecols=["STRUCTURE_NAME", "START_X", "START_Y","END_X", "END_Y"], converters={"START_X":float, "START_Y":float, "END_X": float, "END_Y":float})
dict_bridges = bridge_data.transpose().to_dict('list')
bridge_lines = {bridge: np.array(dict_bridges[bridge]).reshape(2,2) for bridge in dict_bridges}

# This file path should link to the data on your machine
folder_path = r"C:\Users\natal\OneDrive\Desktop\Key_bridge_filter_plot\Bridge Result Data\Filtered Data\\"

# The plots in this script are done based on annual data
years = [i for i in range(2018, 2024)]

#They are also split by different ship sizes, based on group discussion
lengths = [150, 180, 215, 250, 275, 300]
box_names = ["150-180", "180-215", "215-250", "250-275", "275-300", "Above 300"]
#Units = meters

# These are the important bridges. If you'd like to quickly create figures for these bridges, loop through this list instead of all bridges
#important_bridges = ["SUNSHINE SKYWAY BRIDGE", "CHESAPEAKE BAY BRIDGE", "FRANCIS SCOTT KEY BRIDGE", "VERZZANO NARROWS BRIDGE"]

# Give each year a different color
colors = ["red", "orange", "yellow", "green", "blue", "purple"]


for bridge in bridge_lines.keys():
        
        # Save the results into a dictionary that will eventually be a dataframe
        results = {i:[] for i in box_names}
        results["Year"] = []
        
        # Read the data stored locally
        data = pd.read_csv(folder_path + bridge + " Data.csv", usecols=["BaseDateTime", "Length", "VesselType"])
        
        # Remove rows with the header
        filtered = data[data["VesselType"] != 'VesselType']
        
        # Put the columns back in
        filtered.columns = ["BaseDateTime", 'VesselType', 'Length']
        
        # Blank values are turned into NaN values by NumPy
        good = filtered.astype({"VesselType":np.float32, "Length":np.float32})
        
        # UPDATED Prepare a new list that will become a Data frame to be used for a nested bar plot that is seaborn applicable 
        nested_bar_data = []
                
        for y, c in zip(years, colors):
            # There will be a bar plot for each year, overlapping with each other
            list_of_counts = []
                
            
            # Pull all the boats from the year
            yearly_boats = good.loc[good["BaseDateTime"].apply(lambda x: x[:4]) == str(y)]["Length"][::2]
            # Read every other broadcast to match the number of trips (2 broadcasts / trip)
            
            # Get a count for the number of boats of a specific size
            for i in range(len(box_names)-1):
                count = sum(np.where( (yearly_boats >= lengths[i]) & (yearly_boats <= lengths[i+1]), 1, 0))
                results[box_names[i]].append(count)
                list_of_counts.append(count)
                
            # Create a count for boats larger than the largest size    
            out_count = sum(np.where( yearly_boats >= lengths[-1], 1, 0))
            results[box_names[-1]].append(out_count)
            list_of_counts.append(out_count)
            
            # Add the year
            results["Year"].append(y)
            
            # UPDATED: for each year, add the year, size category, and count to the nuested_bar_data dictionary
            for i, size_category in enumerate(box_names):
                nested_bar_data.append({
                    "Year": y, 
                    "Size Category": size_category,
                    "Count": list_of_counts[i]                    
                })
            
        # UPDATED: Converts list to data frame for seaborn 
        plot_nested = pd.DataFrame(nested_bar_data)
            
        # UPDATED: Create a nested bar plot with years as the identifier of each bar, hue identifies the different years
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(
            data=plot_nested,
            x="Size Category", y="Count", hue="Year",
            palette="muted", alpha=.6,ax=ax
        )
            
        # # UPDATED: Add counts above each bar
        # ax = g.facet_axis(0, 0)  # facets are figures made up subplots with the same axes, retrieves the axis of the figure
        # for i in ax.patches:# pathces can be used to add shapes or annotations
        #     height = i.get_height() # Gets the height of each bar
        #     if not np.isnan(height):  # Check if height is a valid number
        #         ax.annotate(f'{height}', 
        #                     (i.get_x() + i.get_width() / 2., height), # position of text 
        #                     ha='center', va='bottom', fontsize=9, color='black')

    
        # UPDATED: Label the Plot and save to pdf 
        ax.set_xlabel("Length Range(m)")
        ax.set_ylabel("Count (Annual)")
        ax.set_title(f"Counts of Ship Sizes by Year for {bridge}")
        
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5)) # Moves legend outside of graph 

        plt.tight_layout()
        
        plt.savefig(rf"C:\Users\natal\OneDrive\Desktop\Key_bridge_filter_plot\New Histograms\\Counts of Ship Sizes by Year for {bridge}.pdf", dpi=300, bbox_inches="tight")
        plt.close(fig)
            
        # Write the results to a CSV file
        df = pd.DataFrame(results)
        df.set_index("Year", inplace=True)
        df.to_csv(rf"C:\Users\natal\OneDrive\Desktop\Key_bridge_filter_plot\New Histograms\\ {bridge} Counts.csv")
            
         




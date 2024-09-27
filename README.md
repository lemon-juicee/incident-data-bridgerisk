# JHU-Key-Bridge-Data

## Project Overview
This repository contains data, analysis, and visualizations related to bridge rankings and traffic data for various ship sizes and bridge locations. The project aims to provide insights into bridge usage patterns and rankings based on different criteria.

## Repository Structure

### Main Branch

The main branch contains the following folders:
 - "Initial Filtering Code" -> Contains code that conducts initial filtering of the Marine Cadastre AIS database, removing all ships that are not of interest to our project and retaining everything else. Also contains corresponding data files.
 - "Geographical Filtering Code" -> Contains code that checks for intersections of ship tracks with a geographical boundary and corresponding data files.
 - "Bridge Intersection Code" -> Contains code that checks for intersections of ship tracks with bridges and corresponding data files.
 - "Aberrancy Code" -> Contains code that counts the frequency of ship aberrancy and corresponding data files.
 - "Plots" -> Contains code that generates plots and corresponding data files.

NOTE: Adding content to the Main branch requires the permission of Promit Chakroborty (pchakro1@jhu.edu)

### Archive

Contains all files from the Summer of 2024.

### Instructions for New Branches

Please follow the below instructions for creating new branches:
 - Naming convention to be followed by ALL NEW BRANCHES: "Date_CreatorName_IntendedUse"
 - Do not delete any branches, even if you created them. Deleting a branch requires the permission of Promit Chakroborty (pchakro1@jhu.edu)
 - Only create branches for the following reasons:
   - To work on new code capabilities
   - To share code with team members

**Usage**

To use this data:

1. Navigate to the desired folder based on the analysis you're interested in.
2. For code to accomplish a specific task, refer to the PY files in the corresponding folders.
3. For plots, refer to the PDF files in the Plots folder.
4. For raw data, check the CSV files in the respective folders.
   
## Contributing
If you'd like to contribute to this project, please follow these steps:
1. Fork the repository
2. Create a new branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

## License
[Include license information here]

## Contact
[Include contact information for the project maintainer]

## Acknowledgments
List any acknowledgments or data sources here
Include any relevant citations or references


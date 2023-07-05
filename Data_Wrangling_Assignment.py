#importing the necessary packages
import arcgis
import pandas as pd
import os
import arcpy

# Reading in the data and visualisation
IEC = pd.read_excel(r"C:\Users\charl\Desktop\4th year Honours\GIT713\IEC_Data_Project\Resources\Voters_data.xlsx")

IEC.head()

IEC.tail()

IEC.describe()

IEC.info()

print(IEC.columns)

IEC["Voter Turnout"].min()

# Splitting the data
IEC[['CAT', 'Muncipality']] = IEC['Municipality'].str.split(' - ',expand =True)

# Renaming the columnns 
new_IEC = {col: col.replace(' ', '_') for col in IEC.columns}

Formated_IEC = IEC.rename(columns=new_IEC)

# Re-arranging column headings for the dataset
Format_IEC_data = Formated_IEC.reindex(columns = ['CAT','Muncipality','Registered_Voters','Voter_Turnout','MEC7_Votes','%_Voter_Turnout'])  

Format_IEC_data.head()

# Exporting data to excel
Format_IEC_data.to_excel(r"C:\Users\charl\Desktop\4th year Honours\GIT713\Formated_Voters_Data.xlsx", index=False)

# Reading in the data 
IEC = pd.read_excel(r"Z:\DW Task\IEC_Data_Project\IEC_Data_Project\Resources\Voters_data.xlsx")

# Spliting the municipality data
IEC[['CAT', 'Municipality']] = IEC['Municipality'].str.split(' - ',expand =True)

#Calculating the % voter turnout
IEC['%_Non_voters'] = (1 - IEC['% Voter Turnout'])
IEC['%_Non_voters'] = IEC['%_Non_voters'].astype(float)
IEC.head()

#Renamed my columns by adding an underscore where there is spaces in the name
new_IEC_columns = {col: col.replace(' ', '_') for col in IEC.columns}

IEC = IEC.rename(columns=new_IEC_columns)

format_IEC_data = IEC.reindex(columns = ['CAT','Municipality','Registered_Voters','Voter_Turnout','MEC7_Votes','%_Voter_Turnout', '%_Non_voters'])  


# Create variables that represent the ArcGIS Pro project and map
aprx = arcpy.mp.ArcGISProject("CURRENT")
mp = aprx.listMaps('Map')[0]

# Create a variable that represents the default file geodatabase
wcdb = r"IEC_task.gdb"
aprx.defaultGeodatabase = wcdb
arcpy.env.workspace = wcdb


# Create a variable that represents the county geometry dataset
wc_name = "Wc_mdb"
wc_shp = os.path.join(wcdb, wc_name)

# Load the dataset into a spatially-enabled dataframe
wc_df = pd.DataFrame.spatial.from_featureclass(wc_shp)
wc_df.head()

# Modify the dataframe to only include the attributes that are needed
wc_df = wc_df[['OBJECTID', 'CAT_B', 'OBJECTID','District','SHAPE', 'Shape__Are', 'Shape__Len']]
wc_df.head()

# Join the election dataframe with the county geometry dataframe
merged = pd.merge(format_IEC_data, wc_df, left_on='CAT', right_on='CAT_B', how='left')

# Joining the dataset to the data frame
merged.head()

output_fc_name = 'WC_merged'
output_fc = merged.spatial.to_featureclass(os.path.join(wcdb, output_fc_name))
output_fc

import arcgis
import pandas as pd
import os
import arcpy

wc_ward = pd.read_csv(r"C:\Users\charl\Desktop\4th year Honours\GIT713\DW task 3\Resources\WP.csv")
wc_ward.head()

wc_ward[['Ward','Ward_no']] = wc_ward['Ward'].str.split(' ', expand = True)
wc_ward[['CAT', 'Municipality']] = wc_ward['Municipality'].str.split(' - ', expand = True)

wc_ward = wc_ward.reindex(columns = ['PartyName','Municipality', 'Ward_no', 'CAT','Province',
                                     'BallotType', 'SpoiltVotes','VotingStationName', 'RegisteredVoters', 
                                   'DateGenerated', 'Ward', 'VotingDistrict','TotalValidVotes'])  

# Group the data by municipality and political party
grouped = wc_ward.groupby(['CAT', 'PartyName'])['TotalValidVotes'].sum().reset_index()
grouped.info()

grouped["Rank"] = grouped.groupby('CAT')["TotalValidVotes"].rank(method='dense', ascending = True)

# # Group by CAT column and select the row with the highest rank (i.e., the winning party) for each group
winners = grouped.loc[grouped.groupby('CAT')["Rank"].idxmax()]

# Merge the winners DataFrame with the original grouped DataFrame to add the winning party names as a new column
grouped = pd.merge(grouped, winners[['CAT', 'PartyName']], on='CAT', suffixes=('', '_winner'))

# Filter the wc_ward DataFrame to only include rows for the winning category (CAT) and select PartyName and TotalValidVotes columns
winning_votes = wc_ward[wc_ward['CAT'].isin(winners['CAT'])][['PartyName', 'TotalValidVotes']]

# Group by PartyName and sum the TotalValidVotes column
winning_votes = winning_votes.groupby('PartyName')['TotalValidVotes'].sum().reset_index()

# Merge the winning_votes DataFrame with the grouped DataFrame based on the PartyName column
grouped = pd.merge(grouped, winning_votes, on='PartyName', suffixes=('', '_votes'))

grouped.info()

# sort the grouped DataFrame by CAT and TotalValidVotes
grouped = grouped.sort_values(['CAT', 'TotalValidVotes'], ascending=[True, False])

# use groupby and apply to get the second highest TotalValidVotes for each CAT
second_highest_votes = grouped.groupby('CAT')['TotalValidVotes'].apply(lambda x: x.nlargest(2).iloc[-1]).reset_index()

# merge the second_highest_votes DataFrame with the grouped DataFrame to get the PartyName for each CAT
second_place = pd.merge(grouped, second_highest_votes, on=['CAT', 'TotalValidVotes'])

# filter the second_place DataFrame to only include the rows where TotalValidVotes equals the second highest TotalValidVotes for that CAT
second_place = second_place[second_place['TotalValidVotes'] == second_place['TotalValidVotes']]

# select the PartyName and CAT columns
second_place = second_place[['PartyName', 'CAT', 'TotalValidVotes']]


aprx = arcpy.mp.ArcGISProject("CURRENT")
mp = aprx.listMaps('MAP1')[0]

# Create a variable that represents the default file geodatabase
fgdb = r"DW_Task3_Pro.gdb"
aprx.defaultGeodatabase = fgdb
arcpy.env.workspace = fgdb

counties_fc_name = "Wc_MDB"
counties_fc = os.path.join(fgdb, counties_fc_name)

counties_df = pd.DataFrame.spatial.from_featureclass(counties_fc)
counties_df.head()
counties_df.columns

# Only merge one data frame at a time. So comment out the dataframe you dont want to obtain

# This line below merges the dataframe with the party that came first with the counties data frame 
geo_df = pd.merge(grouped, counties_df, left_on='CAT', right_on="CAT_B", how='left')


#This line below merges the dataframe with the parties that came second with the counties data frame
# geo_df = pd.merge(second_place, counties_df, left_on='CAT', right_on="CAT_B", how='left')

# Visualize the merged data
geo_df.head()

# Printing out the final shapefile
out_2016_fc_name = "ELECTIONRESULTS_SECOND"
out_2016_fc = geo_df.spatial.to_featureclass(os.path.join(fgdb, out_2016_fc_name))
out_2016_fc

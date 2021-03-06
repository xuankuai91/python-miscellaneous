# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Crime Incident Locator.py
# Created on: 2017-03-01 13:13
#   (generated by ArcGIS/ModelBuilder)
# Modified on: 2017-04-05 13:26
#   (edited by Xuan Kuai)
# Description: This program is used for identifying which council district,
#   crime prevention district and ZIP code area each crime incient happened
#   in, in East Baton Rouge Parish.
# ---------------------------------------------------------------------------

# Import modules
import arcpy
from arcpy import env

import datetime as dt
from datetime import timedelta

import os, urllib
import pandas as pd
import numpy as np

# Set working directory
cwd = sys.path[0] # Get the current working directory that contains the script
os.chdir(cwd)
env.workspace = os.path.join(cwd, "Crime_Data.gdb")
env.overwriteOutput = True # Overwrite output

# Get the latest crime record date:
in_Date = (dt.date.today() - timedelta(days = 12)).strftime("%Y-%m-%d")

# Convert Socrata query to CSV
in_URL = "https://data.brla.gov/resource/5rji-ddnu.csv?offense_date=" + in_Date + "T00:00:00.000"
in_Query = (in_URL)
in_Cols = ["file_number", "offense_date", "offense_time", "crime", "a_c", "offense", "offense_desc", "address", "st_number", "st_dir", "st_name", "st_type", "city", "state", "zip", "district", "zone", "subzone", "complete_district"]

in_CrimeRec_Raw = pd.read_csv(in_Query, dtype = object, usecols = in_Cols)
in_CrimeRec_Raw["offense_date"] = in_CrimeRec_Raw["offense_date"].map(lambda x: x[:10]) # Remove trailing text
in_CrimeRec_Raw["offense_date"] = in_CrimeRec_Raw["offense_date"].map(lambda x: pd.to_datetime(x, format = '%Y-%m-%d')).dt.strftime('%m/%d/%Y') # Convert date format
in_CrimeRec_Raw = in_CrimeRec_Raw[in_Cols] # Force column order
in_CrimeRec_Raw.columns = map(lambda x: x.upper(), in_Cols) # Force column header uppercase

with open("Baton_Rouge_Crime_Incidents_Current.csv", "w") as f:
    in_CrimeRec_Raw.to_csv(f, index = False)

# Create the ArcGIS Server connection file
ServerURL = "http://maps.brla.gov/gis/services"
ASConnFile_Name = "gis_maps_brla_gov.ags"
ASConnFile = os.path.join(cwd, ASConnFile_Name)
arcpy.mapping.CreateGISServerConnectionFile(
    "USE_GIS_SERVICES",
    cwd,
    ASConnFile_Name,
    ServerURL,
    "ARCGIS_SERVER",
    username = "",
    password = ""
)

in_Geocoder = os.path.join(ASConnFile, "EBRP_Composite_Locator") # Get the geocoder

# Process: Create Database Connection
DBConnFile_Name = "Enterprise.sde"
DBConnFile = os.path.join(cwd, DBConnFile_Name)
arcpy.CreateDatabaseConnection_management(
    cwd,
    DBConnFile_Name,
    "ORACLE",
    "ebrgis.brgov.net",
    "DATABASE_AUTH",
    "BR_ENTERPRISE_VIEWER",
    "Intergraph#1",
    "SAVE_USERNAME",
    "",
    "SDE",
    "TRANSACTIONAL",
    "SDE.DEFAULT",
    ""
)

# Get the enterprise database layers
in_Council_Pg = os.path.join(DBConnFile, "BR_ENTERPRISE_USER.DISTRICT_COUNCIL")
in_CrimePrev_Pg = os.path.join(DBConnFile, "BR_ENTERPRISE_USER.DISTRICT_CRIME_PREVENT")
in_ZIP_Pg = os.path.join(DBConnFile, "BR_ENTERPRISE_USER.ZIP")
in_Neighborhood_Pg = os.path.join(DBConnFile, "BR_ENTERPRISE_USER.NEIGHBORHOOD")

# Local variables:
in_CrimeRec = os.path.join(cwd, "Baton_Rouge_Crime_Incidents_Current.csv")
CrimeIncid_Pt_Init = "BR_CrimeIncid_Pt_Init"
CrimeIncid_Pt = "BR_CrimeIncid_Pt"
CrimeIncid_Pt_WGS = "BR_CrimeIncid_Pt_WGS"
CrimeIncid_Pt_Council = "BR_CrimeIncid_Pt_Council"
CrimeIncid_Pt_Council_CrimePrev = "BR_CrimeIncid_Pt_Council_CrimePrev"
CrimeIncid_Pt_Council_CrimePrev_ZIP = "BR_CrimeIncid_Pt_Council_CrimePrev_ZIP"
CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood = "BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood"

# Process: Geocode Addresses
arcpy.GeocodeAddresses_geocoding(
    in_CrimeRec,
    in_Geocoder,
    "'Single Line Input' Address VISIBLE NONE",
    CrimeIncid_Pt_Init,
    "STATIC"
)

# Process: Make Feature Layer - Matched crime incident locations
arcpy.MakeFeatureLayer_management(
    CrimeIncid_Pt_Init,
    "Matched_Pt_Temp",
    "Status = 'M'",
    "",
    ""
)

# Process: Copy Features
arcpy.CopyFeatures_management(
    "Matched_Pt_Temp",
    CrimeIncid_Pt,
    "",
    "0",
    "0",
    "0"
)

# Process: Add Field - Latitude
arcpy.AddField_management(
    CrimeIncid_Pt,
    "Lat",
    "DOUBLE",
    "",
    "",
    "",
    "",
    "NULLABLE",
    "NON_REQUIRED",
    ""
)

# Process: Add Field - Longitude
arcpy.AddField_management(
    CrimeIncid_Pt,
    "Lon",
    "DOUBLE",
    "",
    "",
    "",
    "",
    "NULLABLE",
    "NON_REQUIRED",
    ""
)

# Process: Add Field - Council District
arcpy.AddField_management(
    CrimeIncid_Pt,
    "Council",
    "LONG",
    "",
    "",
    "",
    "",
    "NULLABLE",
    "NON_REQUIRED",
    ""
)

# Process: Add Field - Crime Prevention District
arcpy.AddField_management(
    CrimeIncid_Pt,
    "CrimePrev",
    "TEXT",
    "",
    "",
    "",
    "",
    "NULLABLE",
    "NON_REQUIRED",
    ""
)

# Process: Add Field - ZIP
arcpy.AddField_management(
    CrimeIncid_Pt,
    "ZIP_Code",
    "TEXT",
    "",
    "",
    "",
    "",
    "NULLABLE",
    "NON_REQUIRED",
    ""
)

# Process: Add Field - Neighborhood
arcpy.AddField_management(
    CrimeIncid_Pt,
    "Neighborhood",
    "TEXT",
    "",
    "",
    "",
    "",
    "NULLABLE",
    "NON_REQUIRED",
    ""
)

# Process: Project
arcpy.Project_management(
    CrimeIncid_Pt,
    CrimeIncid_Pt_WGS,
    "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
    "WGS_1984_(ITRF00)_To_NAD_1983",
    "PROJCS['NAD_1983_StatePlane_Louisiana_South_FIPS_1702_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',3280833.333333333],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-91.33333333333333],PARAMETER['Standard_Parallel_1',29.3],PARAMETER['Standard_Parallel_2',30.7],PARAMETER['Latitude_Of_Origin',28.5],UNIT['Foot_US',0.3048006096012192]]",
    "NO_PRESERVE_SHAPE",
    "",
    "NO_VERTICAL"
)

# Process: Calculate Field - Latitude
arcpy.CalculateField_management(
    CrimeIncid_Pt_WGS,
    "Lat",
    "!shape.firstpoint.Y!",
    "PYTHON_9.3",
    ""
)

# Process: Calculate Field - Longitude
arcpy.CalculateField_management(
    CrimeIncid_Pt_WGS,
    "Lon",
    "!shape.firstpoint.X!",
    "PYTHON_9.3",
    ""
)

# Add Council District Attribute
# Process: Copy Features
arcpy.CopyFeatures_management(
    in_Council_Pg,
    "Council_Pg_Temp",
    "",
    "0",
    "0",
    "0"
)

# Process: Spatial Join
arcpy.SpatialJoin_analysis(
    CrimeIncid_Pt_WGS,
    "Council_Pg_Temp",
    CrimeIncid_Pt_Council,
    "JOIN_ONE_TO_ONE",
    "KEEP_ALL",
    "",
    "WITHIN",
    "",
    ""
)

# Process: Calculate Field
arcpy.CalculateField_management(
    CrimeIncid_Pt_Council,
    "Council",
    "!DISTRICT_NUM!",
    "PYTHON_9.3",
    ""
)

# Add Crime Prevention District Attribute
# Process: Copy Features
arcpy.CopyFeatures_management(
    in_CrimePrev_Pg,
    "CrimePrev_Pg_Temp",
    "",
    "0",
    "0",
    "0"
)

# Process: Spatial Join
arcpy.SpatialJoin_analysis(
    CrimeIncid_Pt_Council,
    "CrimePrev_Pg_Temp",
    CrimeIncid_Pt_Council_CrimePrev,
    "JOIN_ONE_TO_ONE",
    "KEEP_ALL",
    "",
    "WITHIN",
    "",
    ""
)

# Process: Calculate Field
arcpy.CalculateField_management(
    CrimeIncid_Pt_Council_CrimePrev,
    "CrimePrev",
    "!NAME!",
    "PYTHON_9.3",
    ""
)

# Add ZIP Attribute
# Process: Copy Features
arcpy.CopyFeatures_management(
    in_ZIP_Pg,
    "ZIP_Pg_Temp",
    "",
    "0",
    "0",
    "0"
)

# Process: Spatial Join
arcpy.SpatialJoin_analysis(
    CrimeIncid_Pt_Council_CrimePrev,
    "ZIP_Pg_Temp",
    CrimeIncid_Pt_Council_CrimePrev_ZIP,
    "JOIN_ONE_TO_ONE",
    "KEEP_ALL",
    "",
    "WITHIN",
    "",
    ""
)

# Process: Calculate Field
arcpy.CalculateField_management(
    CrimeIncid_Pt_Council_CrimePrev_ZIP,
    "ZIP_Code",
    "!ZIP_CODE_1!",
    "PYTHON_9.3",
    ""
)

# Add Neighborhood Attribute
# Process: Copy Features
arcpy.CopyFeatures_management(
    in_Neighborhood_Pg,
    "Neighborhood_Pg_Temp",
    "",
    "0",
    "0",
    "0"
)

# Process: Spatial Join
arcpy.SpatialJoin_analysis(
    CrimeIncid_Pt_Council_CrimePrev_ZIP,
    "Neighborhood_Pg_Temp",
    CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,
    "JOIN_ONE_TO_ONE",
    "KEEP_ALL",
    "",
    "WITHIN",
    "",
    ""
)

# Process: Calculate Field
arcpy.CalculateField_management(
    CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,
    "Neighborhood",
    "!NEIGHBORHOOD_1!",
    "PYTHON_9.3",
    ""
)

# Process: Table to Table
arcpy.TableToTable_conversion(
    CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,
    cwd,
    "Temp.csv",
    "",
    "FILE_NUMBE \"FILE NUMBER\" true true false 4 Long 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,FILE_NUMBER,-1,-1;OFFENSE_DA \"OFFENSE DATE\" true true false 8 Date 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,OFFENSE_DATE,-1,-1;OFFENSE_TI \"OFFENSE TIME\" true true false 4 Long 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,OFFENSE_TIME,-1,-1;CRIME \"CRIME\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,CRIME,-1,-1;COMMITTED \"COMMITTED\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,COMMITTED,-1,-1;OFFENSE \"OFFENSE\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,OFFENSE,-1,-1;OFFENSE_DE \"OFFENSE DESC\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,OFFENSE_DESC,-1,-1;ADDRESS \"ADDRESS\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,ADDRESS,-1,-1;ST_NUMBER \"ST NUMBER\" true true false 4 Long 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,ST_NUMBER,-1,-1;ST_DIR \"ST DIR\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,ST_DIR,-1,-1;ST_NAME \"ST NAME\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,ST_NAME,-1,-1;ST_TYPE \"ST TYPE\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,ST_TYPE,-1,-1;CITY \"CITY\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,CITY,-1,-1;STATE \"STATE\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,STATE,-1,-1;ZIP \"ZIP\" true true false 4 Long 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,ZIP,-1,-1;DISTRICT \"DISTRICT\" true true false 4 Long 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,DISTRICT,-1,-1;ZONE \"ZONE\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,ZONE,-1,-1;SUBZONE \"SUBZONE\" true true false 4 Long 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,SUBZONE,-1,-1;COMPLETE_D \"COMPLETE DISTRICT\" true true false 8000 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,COMPLETE_DISTRICT,-1,-1;Lat \"Lat\" true true false 8 Double 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,Lat,-1,-1;Lon \"Lon\" true true false 8 Double 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,Lon,-1,-1;Council \"Council\" true true false 4 Long 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,Council,-1,-1;CrimePrev \"CrimePrev\" true true false 255 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,CrimePrev,-1,-1;ZIP_Code \"ZIP_Code\" true true false 255 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,ZIP_Code,-1,-1;Neighborho \"Neighborho\" true true false 255 Text 0 0 ,First,#,X:\\Crime_Incid\\Crime_Data.gdb\\BR_CrimeIncid_Pt_Council_CrimePrev_ZIP_Neighborhood,Neighborhood,-1,-1",
    ""
)

# Process: Delete
for fc in arcpy.ListFeatureClasses():
    arcpy.Delete_management(fc)

# Append records
in_CSV = pd.read_csv("Temp.csv")
del in_CSV["OID"] # Delete unwanted columns
HeaderCSV = "Baton_Rouge_Crime_Incidents.csv"
with open("Baton_Rouge_Crime_Incidents.csv", "a") as f:
    in_CSV.to_csv(f, header = False, index = False)

# Delete temporary files
for TempFile in ("gis_maps_brla_gov.ags", "Enterprise.sde", "Baton_Rouge_Crime_Incidents_Current.csv", "Temp.csv", "Temp.txt.xml", "schema.ini"):
    os.remove(TempFile)

import arcpy, datetime, os
import pandas as pd

def main():
    work_directory = r"\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Process Automation\Project Folder\Tools and Applications\ACS Data"
    arcpy.env.workspace = os.path.join(work_directory, "Default.gdb")
    arcpy.env.overwriteOutput = True

    units = [["Block_Groups", "BG"], ["Counties", "COUNTY"], ["Places", "PLACE"], ["Tracts", "TRACT"], ["Zip_Codes", "ZCTA"]]

    for unit in units:
        print("    USCB_ACS_2018_5Yr_" + unit[0])
        sde_layer = "USCB_ACS_2018_5Yr_" + unit[0]
        arcpy.MakeFeatureLayer_management(sde_layer, 'sde_fl')

        gdb = os.path.join(work_directory, "ACS_" + acs_year + "_5YR_" + unit[1] + ".gdb")

        # Calculate population by age data
        print("        Calculating population by age data ...")
        x01_table = os.path.join(gdb, "X01_AGE_AND_SEX")
        arcpy.AddJoin_management('sde_fl', "GEOID_Data", x01_table, "GEOID")

        print("            Total population")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Tot_Pop", "[X01_AGE_AND_SEX.B01001e1]")

        print("            Population under 18")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Age_U18", "[X01_AGE_AND_SEX.B01001e3] + [X01_AGE_AND_SEX.B01001e4] + [X01_AGE_AND_SEX.B01001e5] + [X01_AGE_AND_SEX.B01001e6] + [X01_AGE_AND_SEX.B01001e27] + [X01_AGE_AND_SEX.B01001e28] + [X01_AGE_AND_SEX.B01001e29] + [X01_AGE_AND_SEX.B01001e30]")

        print("            Population between 18 - 24")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Age_18_64", "[X01_AGE_AND_SEX.B01001e7] + [X01_AGE_AND_SEX.B01001e8] + [X01_AGE_AND_SEX.B01001e9] + [X01_AGE_AND_SEX.B01001e10] + [X01_AGE_AND_SEX.B01001e11] + [X01_AGE_AND_SEX.B01001e12] + [X01_AGE_AND_SEX.B01001e13] + [X01_AGE_AND_SEX.B01001e14] + [X01_AGE_AND_SEX.B01001e15] + [X01_AGE_AND_SEX.B01001e16] + [X01_AGE_AND_SEX.B01001e17] + [X01_AGE_AND_SEX.B01001e18] + [X01_AGE_AND_SEX.B01001e19] + [X01_AGE_AND_SEX.B01001e31] + [X01_AGE_AND_SEX.B01001e32] + [X01_AGE_AND_SEX.B01001e33] + [X01_AGE_AND_SEX.B01001e34] + [X01_AGE_AND_SEX.B01001e35] + [X01_AGE_AND_SEX.B01001e36] + [X01_AGE_AND_SEX.B01001e37] + [X01_AGE_AND_SEX.B01001e38] + [X01_AGE_AND_SEX.B01001e39] + [X01_AGE_AND_SEX.B01001e40] + [X01_AGE_AND_SEX.B01001e41] + [X01_AGE_AND_SEX.B01001e42] + [X01_AGE_AND_SEX.B01001e43]")

        print("            Population above 65")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Age_65Plus", "[X01_AGE_AND_SEX.B01001e20] + [X01_AGE_AND_SEX.B01001e21] + [X01_AGE_AND_SEX.B01001e22] + [X01_AGE_AND_SEX.B01001e23] + [X01_AGE_AND_SEX.B01001e24] + [X01_AGE_AND_SEX.B01001e25] + [X01_AGE_AND_SEX.B01001e44] + [X01_AGE_AND_SEX.B01001e45] + [X01_AGE_AND_SEX.B01001e46] + [X01_AGE_AND_SEX.B01001e47] + [X01_AGE_AND_SEX.B01001e48] + [X01_AGE_AND_SEX.B01001e49]")
        arcpy.RemoveJoin_management('sde_fl')

        # Calculating population by race data
        print("        Calculating population by race data")
        x02_table = os.path.join(gdb, "X02_RACE")
        arcpy.AddJoin_management('sde_fl', "GEOID_Data", x02_table, "GEOID")

        print("            Asian population")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Asian", "[X02_RACE.B02001e5]")

        print("            Black population")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Black", "[X02_RACE.B02001e3]")

        print("            White population")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".White", "[X02_RACE.B02001e2]")

        print("            Other population")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Other", "[X02_RACE.B02001e4] + [X02_RACE.B02001e6] + [X02_RACE.B02001e7] + [X02_RACE.B02001e8]")
        arcpy.RemoveJoin_management('sde_fl')

        # Calculate Hispanic population data
        print("        Calculating Hispanic population data")
        x03_table = os.path.join(gdb, "X03_HISPANIC_OR_LATINO_ORIGIN")
        arcpy.AddJoin_management('sde_fl', "GEOID_Data", x03_table, "GEOID")

        print("            Hispanic population")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Hispanic", "[X03_HISPANIC_OR_LATINO_ORIGIN.B03001e3]")
        arcpy.RemoveJoin_management('sde_fl')

        # Calculate household data
        print("        Calculating household data")
        x11_table = os.path.join(gdb, "X11_HOUSEHOLD_FAMILY_SUBFAMILIES")
        arcpy.AddJoin_management('sde_fl', "GEOID_Data", x11_table, "GEOID")

        print("            Number of households")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Households", "[X11_HOUSEHOLD_FAMILY_SUBFAMILIES.B11001e1]")
        arcpy.RemoveJoin_management('sde_fl')

        # Calculate income data
        print("        Calculating income data")
        x19_table = os.path.join(gdb, "X19_INCOME")
        arcpy.AddJoin_management('sde_fl', "GEOID_Data", x19_table, "GEOID")

        print("            Median household income")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Med_HH_Inc", "[X19_INCOME.B19013e1]")
        arcpy.RemoveJoin_management('sde_fl')

        # Calculate housing unit data
        print("        Calculating housing unit data")
        x25_table = os.path.join(gdb, "X25_HOUSING_CHARACTERISTICS")
        arcpy.AddJoin_management('sde_fl', "GEOID_Data", x25_table, "GEOID")

        print("            Number of housing units")
        arcpy.CalculateField_management('sde_fl', "USCB_ACS_2018_5Yr_" + unit[0] + ".Housing_Un", "[X25_HOUSING_CHARACTERISTICS.B25001e1]")
        arcpy.RemoveJoin_management('sde_fl')

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Cell Sector Check tool")
    print("Version 1.0")
    print("Last update: 7/28/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    acs_year = raw_input("Please enter ACS year (yyyy): ")
    main() # Run main function

    end_time = datetime.datetime.now()
    print("\n")
    print("End time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

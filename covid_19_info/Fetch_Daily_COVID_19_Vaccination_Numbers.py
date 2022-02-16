import arcpy, datetime
import pandas as pd

def fetch_dshs_5_plus_vaccination_numbers(table, county):
    query = "{} = '{}'".format(arcpy.AddFieldDelimiters(table, "NAME"), county)
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch vaccination data from DSHS
    url = "https://dshs.texas.gov/immunize/covid19/COVID-19-Vaccine-Data-by-County.xls"
    df = pd.read_excel(url, 'By County')

    for index in df.index:
        if df["County Name"][index] == county:
            no_of_doses_5 = df["Vaccine Doses Administered"][index]
            pop5_1plus_doses = df["People Vaccinated with at least One Dose"][index]
            pop5_fully_vac = df["People Fully Vaccinated"][index]
            pop5_booster = df["People Vaccinated with Booster Dose"][index]
    
    print("            No_of_Doses_5")
    arcpy.CalculateField_management('table_tv', "No_of_Doses_5", str(no_of_doses_5))

    print("            Pop5_1plus_Doses")
    arcpy.CalculateField_management('table_tv', "Pop5_1plus_Doses", str(pop5_1plus_doses))

    print("            Pop5_Fully_Vac")
    arcpy.CalculateField_management('table_tv', "Pop5_Fully_Vac", str(pop5_fully_vac))

    print("            Pop5_Booster")
    arcpy.CalculateField_management('table_tv', "Pop5_Booster", str(pop5_booster))

    # Calculate percentages
    arcpy.SelectLayerByAttribute_management('table_tv', "CLEAR_SELECTION")

    print("            Pct5_1plus_Doses")
    arcpy.CalculateField_management('table_tv', "Pct5_1plus_Doses", "100 * [Pop5_1plus_doses] / [Pop_5plus]")

    print("            Pct5_Fully_Vac")
    arcpy.CalculateField_management('table_tv', "Pct5_Fully_Vac", "100 * [Pop5_Fully_Vac] / [Pop_5plus]")

    print("            Pct5_Booster")
    arcpy.CalculateField_management('table_tv', "Pct5_Booster", "100 * [Pop5_Booster] / [Pop_5plus]")

def fetch_dshs_65_plus_vaccination_numbers(table, county):
    query = "{} = '{}'".format(arcpy.AddFieldDelimiters(table, "NAME"), county)
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch vaccination data from DSHS
    url = "https://dshs.texas.gov/immunize/covid19/COVID-19-Vaccine-Data-by-County.xls"
    df = pd.read_excel(url, 'By County, Age')

    no_of_doses_65 = 0
    pop65_1plus_doses = 0
    pop65_fully_vac = 0
    pop65_booster = 0

    for index in df.index:
        if df["County Name "][index] == county and df["Age Group"][index] in ("65-79", "80+"):
            no_of_doses_65 += df["Doses Administered"][index]
            pop65_1plus_doses += df["People Vaccinated with at least One Dose"][index]
            pop65_fully_vac += df["People Fully Vaccinated "][index]
            pop65_booster += df["People with Booster Dose"][index]
    
    print("            No_of_Doses_65")
    arcpy.CalculateField_management('table_tv', "No_of_Doses_65", str(no_of_doses_65))

    print("            Pop65_1plus_Doses")
    arcpy.CalculateField_management('table_tv', "Pop65_1plus_Doses", str(pop65_1plus_doses))

    print("            Pop65_Fully_Vac")
    arcpy.CalculateField_management('table_tv', "Pop65_Fully_Vac", str(pop65_fully_vac))

    print("            Pop65_Booster")
    arcpy.CalculateField_management('table_tv', "Pop65_Booster", str(pop65_booster))

    # Calculate percentages
    arcpy.SelectLayerByAttribute_management('table_tv', "CLEAR_SELECTION")

    print("            Pct65_1plus_Doses")
    arcpy.CalculateField_management('table_tv', "Pct65_1plus_Doses", "100 * [Pop65_1plus_doses] / [Pop_65plus]")

    print("            Pct65_Fully_Vac")
    arcpy.CalculateField_management('table_tv', "Pct65_Fully_Vac", "100 * [Pop65_Fully_Vac] / [Pop_65plus]")

    print("            Pct65_Booster")
    arcpy.CalculateField_management('table_tv', "Pct65_Booster", "100 * [Pop65_Booster] / [Pop_65plus]")

def main():
    workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    day = datetime.datetime.today()
    date = "{}/{}/{}".format(day.year, day.month, day.day)

    table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Info\Global.GLOBAL_ADMIN.HGAC_Counties_COVID_19_Vaccination_Info"

    print("    HGAC_Counties_COVID_19_Vaccination_Info")
    counties = ["Austin", "Brazoria", "Chambers", "Colorado", "Fort Bend", "Galveston", "Harris", "Liberty", "Matagorda", "Montgomery", "Walker", "Waller", "Wharton"]
    for county in counties:
        print("        " + county)
        fetch_dshs_5_plus_vaccination_numbers(table, county)
        fetch_dshs_65_plus_vaccination_numbers(table, county)

    arcpy.CalculateField_management(table, "Last_Updated", "CDate(#{}#)".format(date))

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Fetch Daily COVID-19 Vaccination Numbers tool ...")
    print("Version 1.0")
    print("Last update: 2/16/2022")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

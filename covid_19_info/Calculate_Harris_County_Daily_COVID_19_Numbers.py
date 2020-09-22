import arcpy, datetime

def calculate_harris_table(table, county_summary, day):
    fields = ["NAME", "No_of_Cases", "No_of_Actives", "No_of_Deaths", "No_of_Recoveries", "No_of_Tests"]
    harris_query = arcpy.AddFieldDelimiters(county_summary, "NAME") + " = 'Harris'"

    harris_cursor = arcpy.da.SearchCursor(county_summary, fields, harris_query)
    for harris_row in harris_cursor:
        confirmed_cases = harris_row[1]
        active_cases = harris_row[2]
        deceased_cases = harris_row[3]
        recovered_cases = harris_row[4]
        tests = harris_row[5]

    # Compose date query of the day before the execution date (for the latest cases data)
    this_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(day.year, day.month, day.day)
    this_day_query = arcpy.AddFieldDelimiters(table, "Date_") + " = " + this_day_date

    # Compose date query of two days before the execution date (for the previous cases data and the latest tests data)
    previous_day = day - datetime.timedelta(1)
    previous_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(previous_day.year, previous_day.month, previous_day.day)
    previous_day_query = arcpy.AddFieldDelimiters(table, "Date_") + " = " + previous_day_date

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    # Copy the latest cases data from HGAC_Counties_COVID_19_Cases to HGAC_COVID_19_Harris_County_Info
    print("        Confirmed")
    arcpy.CalculateField_management('table_tv', "Confirmed", str(confirmed_cases))

    print("        Active")
    arcpy.CalculateField_management('table_tv', "Active", str(active_cases))

    print("        Deceased")
    arcpy.CalculateField_management('table_tv', "Deceased", str(deceased_cases))

    print("        Recovered")
    arcpy.CalculateField_management('table_tv', "Recovered", str(recovered_cases))

    # Calculate fatality rate
    print("        Fatality_Rate")
    arcpy.CalculateField_management('table_tv', "Fatality_Rate", "100 * [Deceased] / [Confirmed]")

    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", previous_day_query)

    # Copy the latest tests data from HGAC_Counties_COVID_19_Cases to HGAC_COVID_19_Harris_County_Info
    print("        Tests")
    arcpy.CalculateField_management('table_tv', "Tests", str(tests))

    # Calculate changes in cases
    previous_day_cursor = arcpy.da.SearchCursor(table, ["Date_", "Confirmed", "Active", "Deceased", "Recovered", "Tests"], previous_day_query)
    for previous_day_row in previous_day_cursor:
        confirmed_change = confirmed_cases - previous_day_row[1] 
        active_change = active_cases - previous_day_row[2]
        deceased_change = deceased_cases - previous_day_row[3]
        recovered_change = recovered_cases - previous_day_row[4]

    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    print("        Confirmed_Change")
    arcpy.CalculateField_management('table_tv', "Confirmed_Change", str(confirmed_change))

    print("        Active_Change")
    arcpy.CalculateField_management('table_tv', "Active_Change", str(active_change))

    print("        Deceased_Change")
    arcpy.CalculateField_management('table_tv', "Deceased_Change", str(deceased_change))

    print("        Recovered_Change")
    arcpy.CalculateField_management('table_tv', "Recovered_Change", str(recovered_change))

    # Compose date query of three days before the execution date (for the previous tests data)
    previous_2_day = day - datetime.timedelta(2)
    previous_2_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(previous_2_day.year, previous_2_day.month, previous_2_day.day)
    previous_2_day_query = arcpy.AddFieldDelimiters(table, "Date_") + " = " + previous_2_day_date

    # Calculate total and daily positivity rates, and changes in tests
    previous_2_day_cursor = arcpy.da.SearchCursor(table, ["Date_", "Tests"], previous_2_day_query)
    for previous_2_day_row in previous_2_day_cursor:
        tests_change = tests - previous_2_day_row[1]

    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", previous_day_query)

    print("        Tests_Change")
    arcpy.CalculateField_management('table_tv', "Tests_Change", str(tests_change))

    print("        Positivity")
    arcpy.CalculateField_management('table_tv', "Positivity", "100 * [Confirmed] / [Tests]")

    print("        Positivity_Daily")
    arcpy.CalculateField_management('table_tv', "Positivity_Daily", "100 * [Confirmed_Change] / [Tests_Change]")

    # Compose date query of the 14-day period from 2 weeks before the execution date to the previous day of the execution date
    past_2_weeks_day = day - datetime.timedelta(13)
    past_2_weeks_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(past_2_weeks_day.year, past_2_weeks_day.month, past_2_weeks_day.day)
    past_2_weeks_query = arcpy.AddFieldDelimiters(table, "Date_") + " BETWEEN " + past_2_weeks_day_date + " AND " + this_day_date

    # Calculate 14-day average changes in cases
    past_2_weeks_cursor = arcpy.da.SearchCursor(table, ["Date_", "Confirmed_Change", "Active_Change", "Deceased_Change", "Recovered_Change"], past_2_weeks_query)

    confirmed_change_list = []
    active_change_list = []
    deceased_change_list = []
    recovered_change_list = []

    for past_2_weeks_row in past_2_weeks_cursor:
        if past_2_weeks_row[1] is not None:
            confirmed_change_list.append(past_2_weeks_row[1])

        if past_2_weeks_row[2] is not None:
            active_change_list.append(past_2_weeks_row[2])
        
        if past_2_weeks_row[3] is not None:
            deceased_change_list.append(past_2_weeks_row[3])
        
        if past_2_weeks_row[4] is not None:
            recovered_change_list.append(past_2_weeks_row[4])

    confirmed_moving_average = float(sum(confirmed_change_list)) / len(confirmed_change_list)
    active_moving_average = float(sum(active_change_list)) / len(active_change_list)
    deceased_moving_average = float(sum(deceased_change_list)) / len(deceased_change_list)
    recovered_moving_average = float(sum(recovered_change_list)) / len(recovered_change_list)

    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    print("        Confirmed_Mov_Avg")
    arcpy.CalculateField_management('table_tv', "Confirmed_Mov_Avg", str(confirmed_moving_average))

    print("        Active_Mov_Avg")
    arcpy.CalculateField_management('table_tv', "Active_Mov_Avg", str(active_moving_average))

    print("        Deceased_Mov_Avg")
    arcpy.CalculateField_management('table_tv', "Deceased_Mov_Avg", str(deceased_moving_average))

    print("        Recovered_Mov_Avg")
    arcpy.CalculateField_management('table_tv', "Recovered_Mov_Avg", str(recovered_moving_average))

    print("        Positivity_Mov_Avg")
    # Compose date query of the 14-day period from 2 weeks before the previous day of the execution date to two days before the execution date
    previous_2_weeks_day = day - datetime.timedelta(14)
    previous_2_weeks_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(previous_2_weeks_day.year, previous_2_weeks_day.month, previous_2_weeks_day.day)
    previous_2_weeks_query = arcpy.AddFieldDelimiters(table, "Date_") + " BETWEEN " + previous_2_weeks_day_date + " AND " + previous_day_date

    # Calculate 14-day average positivity rate
    previous_2_weeks_cursor = arcpy.da.SearchCursor(table, ["Date_", "Confirmed_Change", "Tests_Change"], previous_2_weeks_query)

    confirmed_change_list_previous_day = []
    tests_change_list = []
    for previous_2_weeks_row in previous_2_weeks_cursor:
        if previous_2_weeks_row[1] is not None:
            confirmed_change_list_previous_day.append(previous_2_weeks_row[1])

        if previous_2_weeks_row[2] is not None:
            tests_change_list.append(previous_2_weeks_row[2])

    positivity_moving_average = 100 * float(sum(confirmed_change_list_previous_day)) / sum(tests_change_list)
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", previous_day_query)
    arcpy.CalculateField_management('table_tv', "Positivity_Mov_Avg", str(positivity_moving_average))

def main():
    arcpy.env.workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.overwriteOutput = True

    yesterday = datetime.datetime.today() - datetime.timedelta(1)

    county_summary = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Info\Global.GLOBAL_ADMIN.HGAC_Counties_COVID_19_Cases"

    # Copy data from HGAC_Counties_COVID_19_Cases to HGAC_COVID_19_Harris_County_Info, and calculate fatality rate, positivity rates, changes in cases, tests, and 7-day averages of changes in cases and positivity rate
    print("    HGAC_COVID_19_Harris_County_Info")
    harris_info_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Harris_County_Info"
    calculate_harris_table(harris_info_table, county_summary, yesterday)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Calculate Harris County Daily COVID-19 Numbers tool")
    print("Version 1.0")
    print("Last update: 9/18/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

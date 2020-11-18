import arcpy, datetime, sys
sys.path.append(r'\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Process Automation\Modules\Bin')
import earcpy

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

    # Compose date query of the execution date (for the latest cases data)
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    # Compose date query of the day before the execution date (for the previous cases data and the latest tests data)
    previous_day = day - datetime.timedelta(1)
    previous_day_query = earcpy.compose_single_date_query(table, "Date_", previous_day, "=")

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
    confirmed_change = earcpy.calculate_difference(table, "Confirmed", this_day_query, previous_day_query)
    active_change = earcpy.calculate_difference(table, "Active", this_day_query, previous_day_query)
    deceased_change = earcpy.calculate_difference(table, "Deceased", this_day_query, previous_day_query)
    recovered_change = earcpy.calculate_difference(table, "Recovered", this_day_query, previous_day_query)

    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    print("        Confirmed_Change")
    arcpy.CalculateField_management('table_tv', "Confirmed_Change", str(confirmed_change))

    print("        Active_Change")
    arcpy.CalculateField_management('table_tv', "Active_Change", str(active_change))

    print("        Deceased_Change")
    arcpy.CalculateField_management('table_tv', "Deceased_Change", str(deceased_change))

    print("        Recovered_Change")
    arcpy.CalculateField_management('table_tv', "Recovered_Change", str(recovered_change))

    # Compose date query of two days before the execution date (for the previous tests data)
    previous_2_day = day - datetime.timedelta(2)
    previous_2_day_query = earcpy.compose_single_date_query(table, "Date_", previous_2_day, "=")

    # Calculate total and daily positivity rates, and changes in tests
    tests_change = earcpy.calculate_difference(table, "Tests", previous_day_query, previous_2_day_query)

    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", previous_day_query)

    print("        Tests_Change")
    arcpy.CalculateField_management('table_tv', "Tests_Change", str(tests_change))

    print("        Positivity")
    arcpy.CalculateField_management('table_tv', "Positivity", "100 * [Confirmed] / [Tests]")

    print("        Positivity_Daily")
    arcpy.CalculateField_management('table_tv', "Positivity_Daily", "100 * [Confirmed_Change] / [Tests_Change]")

    # Compose date query of the 14-day period from 13 days before the execution date to the execution date
    past_2_weeks_query = earcpy.compose_double_date_query(table, "Date_", end_day=day, period=14)
    confirmed_change_list = earcpy.list_values(table, "Confirmed_Change", past_2_weeks_query)
    active_change_list = earcpy.list_values(table, "Active_Change", past_2_weeks_query)
    deceased_change_list = earcpy.list_values(table, "Deceased_Change", past_2_weeks_query)
    recovered_change_list = earcpy.list_values(table, "Recovered_Change", past_2_weeks_query)

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
    previous_2_weeks_query = earcpy.compose_double_date_query(table, "Date_", end_day=previous_day, period=14)
    confirmed_change_list_previous_day = earcpy.list_values(table, "Confirmed_Change", previous_2_weeks_query)
    tests_change_list = earcpy.list_values(table, "Tests_Change", previous_2_weeks_query)

    positivity_moving_average = 100 * float(sum(confirmed_change_list_previous_day)) / sum(tests_change_list)
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", previous_day_query)
    arcpy.CalculateField_management('table_tv', "Positivity_Mov_Avg", str(positivity_moving_average))

def main():
    workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    today = datetime.datetime.today()

    county_summary = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Info\Global.GLOBAL_ADMIN.HGAC_Counties_COVID_19_Cases"

    # Copy data from HGAC_Counties_COVID_19_Cases to HGAC_COVID_19_Harris_County_Info, and calculate fatality rate, positivity rates, changes in cases, tests, and 7-day averages of changes in cases and positivity rate
    print("    HGAC_COVID_19_Harris_County_Info")
    harris_info_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Harris_County_Info"
    calculate_harris_table(harris_info_table, county_summary, today)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Calculate Harris County Daily COVID-19 Numbers tool")
    print("Version 1.2")
    print("Last update: 10/20/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

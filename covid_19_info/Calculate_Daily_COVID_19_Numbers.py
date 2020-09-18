import arcpy, datetime

def copy_case_counts(table, fields, county_summary, day):
    # Insert a new row to table
    target_cursor = arcpy.InsertCursor(table)
    target_row = target_cursor.newRow()

    # Write date of the day before the execution date
    date = "{}/{}/{}".format(day.year, day.month, day.day)
    target_row.setValue("Date_", date)

    # Copy case count from HGAC_Counties_COVID_19_Cases to table
    print("        Counties")
    county_cursor = arcpy.da.SearchCursor(county_summary, fields)

    for county_row in county_cursor:
        county_name = county_row[0]
        value = county_row[1]

        if county_name == "Fort Bend":
            county_name = "Fort_Bend"

        target_row.setValue(county_name, value)

    target_cursor.insertRow(target_row)

def calculate_change(table, day):
    # Calculate total number of cases
    print("        Total")
    arcpy.CalculateField_management(table, "Total", "[Austin] + [Brazoria] + [Chambers] + [Colorado] + [Fort_Bend] + [Galveston] + [Harris] + [Liberty] + [Matagorda] + [Montgomery] + [Walker] + [Waller] + [Wharton]")

    print("        Change")

    # Compose date query of the day before the execution date (for the latest cases data)
    this_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(day.year, day.month, day.day)
    this_day_query = arcpy.AddFieldDelimiters(table, "Date_") + " = " + this_day_date

    # Compose date query of two days before the execution date (for the previous cases data)
    previous_day = day - datetime.timedelta(1)
    previous_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(previous_day.year, previous_day.month, previous_day.day)
    previous_day_query = arcpy.AddFieldDelimiters(table, "Date_") + " = " + previous_day_date

    # Calculate change in cases
    this_day_cursor = arcpy.da.SearchCursor(table, ["Date_", "Total"], this_day_query)
    for this_day_row in this_day_cursor:
        this_day_total = this_day_row[1]

    previous_day_cursor = arcpy.da.SearchCursor(table, ["Date_", "Total"], previous_day_query)
    for previous_day_row in previous_day_cursor:
        previous_day_total = previous_day_row[1]

    change = this_day_total - previous_day_total

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    arcpy.CalculateField_management('table_tv', "Change", str(change))
    
    print("        7-day moving average")

    # Compose date query of the 7-day period from a week before the execution date to the previous day of the execution date
    past_week_day = day - datetime.timedelta(6)
    past_week_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(past_week_day.year, past_week_day.month, past_week_day.day)
    past_week_query = arcpy.AddFieldDelimiters(table, "Date_") + " BETWEEN " + past_week_day_date + " AND " + this_day_date

    # Calculate 7-day average change in cases
    past_week_cursor = arcpy.da.SearchCursor(table, ["Date_", "Change"], past_week_query)
    change_list = [past_week_row[1] for past_week_row in past_week_cursor if past_week_row[1] is not None]
    moving_average = float(sum(change_list)) / len(change_list)

    arcpy.CalculateField_management('table_tv', "Mov_Avg", str(moving_average))

def calculate_test_count(table, county_summary, day):
    print("        Tests")
    county_cursor = arcpy.da.SearchCursor(county_summary, ["NAME", "No_of_Tests"])

    test_list = [county_row[1] for county_row in county_cursor]
    total_tests = sum(test_list)

    # Compose date query of two days before the execution date (for the previous cases data)
    previous_day = day - datetime.timedelta(1)
    previous_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(previous_day.year, previous_day.month, previous_day.day)
    previous_day_query = arcpy.AddFieldDelimiters(table, "Date_") + " = " + previous_day_date

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", previous_day_query)

    arcpy.CalculateField_management('table_tv', "Tests", str(total_tests))

def calculate_table(table, fields, county_summary, day):
    copy_case_counts(table, fields, county_summary, day)
    calculate_change(table, day)

def main():
    arcpy.env.workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.overwriteOutput = True

    yesterday = datetime.datetime.today() - datetime.timedelta(1)

    county_summary = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Info\Global.GLOBAL_ADMIN.HGAC_Counties_COVID_19_Cases"
    arcpy.CalculateField_management(county_summary, "No_of_Cases", "[No_of_Actives] + [No_of_Deaths] + [No_of_Recoveries]") # Calculate total number of cases

    # Copy data from HGAC_Counties_COVID_19_Cases to HGAC_COVID_19_Confirmed_Cases_and_Tests, and calculate total, change, and 7-day average
    print("    HGAC_COVID_19_Confirmed_Cases_and_Tests")
    confirmed_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Confirmed_Cases_and_Tests"
    calculate_table(confirmed_table, ["NAME", "No_of_Cases"], county_summary, yesterday)
    calculate_test_count(confirmed_table, county_summary, yesterday)

    # Copy data from HGAC_Counties_COVID_19_Cases to HGAC_COVID_19_Active_Cases, and calculate total, change, and 7-day average
    print("    HGAC_COVID_19_Active_Cases")
    active_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Active_Cases"
    calculate_table(active_table, ["NAME", "No_of_Actives"], county_summary, yesterday)

    # Copy data from HGAC_Counties_COVID_19_Cases to HGAC_COVID_19_Deceased_Cases, and calculate total, change, and 7-day average
    print("    HGAC_COVID_19_Deceased_Cases")
    deceased_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Deceased_Cases"
    calculate_table(deceased_table, ["NAME", "No_of_Deaths"], county_summary, yesterday)

    # Copy data from HGAC_Counties_COVID_19_Cases to HGAC_COVID_19_Recovered_Cases, and calculate total, change, and 7-day average
    print("    HGAC_COVID_19_Recovered_Cases")
    recovered_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Recovered_Cases"
    calculate_table(recovered_table, ["NAME", "No_of_Recoveries"], county_summary, yesterday)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Calculate Daily COVID-19 Numbers tool")
    print("Version 1.0")
    print("Last update: 9/18/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

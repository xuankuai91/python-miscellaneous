import arcpy, datetime, sys
sys.path.append(r'\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Process Automation\Modules\Bin')
import earcpy

def revise_change(table, day):
    # Calculate total number of cases
    print("            Total")
    # Compose date query of the day intended to revise
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    arcpy.CalculateField_management(table, "Total", "[Austin] + [Brazoria] + [Chambers] + [Colorado] + [Fort_Bend] + [Galveston] + [Harris] + [Liberty] + [Matagorda] + [Montgomery] + [Walker] + [Waller] + [Wharton]")

    print("            Change")
    # Compose date query of the previous day before the day intended to revise
    previous_day = day - datetime.timedelta(1)
    previous_day_query = earcpy.compose_single_date_query(table, "Date_", previous_day, "=")

    # Calculate change in case
    change = earcpy.calculate_difference(table, "Total", this_day_query, previous_day_query)

    arcpy.CalculateField_management('table_tv', "Change", str(change))

    print("            Mov_Avg")

    # Compose date query of the 7-day period from a week before the execution date to the previous day of the execution date
    past_week_query = earcpy.compose_double_date_query(table, "Date_", end_day=day, period=7)

    # Calculate 7-day average change in cases
    change_list = earcpy.list_values(table, "Change", past_week_query)
    moving_average = float(sum(change_list)) / len(change_list)

    arcpy.CalculateField_management('table_tv', "Mov_Avg", str(moving_average))

def revise_positivities(table, day):
    print("            Positivity")
    # Compose date query of the day before the execution date (for the latest cases data)
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)
    arcpy.CalculateField_management('table_tv', "Positivity", "100 * [Total] / [Tests]")

    print("            Positivity_Mov_Avg")
    # Compose date query of the 7-day period from 1 week before the previous day of the execution date to two days before the execution date
    past_week_query = earcpy.compose_double_date_query(table, "Date_", end_day=day, period=7)

    confirmed_change_list = earcpy.list_values(table, "Change", past_week_query)
    tests_change_list = earcpy.list_values(table, "Tests_Change", past_week_query)

    positivity_moving_average = 100 * float(sum(confirmed_change_list)) / sum(tests_change_list)
    arcpy.CalculateField_management('table_tv', "Positivity_Mov_Avg", str(positivity_moving_average))

def copy_counts(table, day, total_confirmed, total_deceased):
    # Compose date query of the iterated date
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    # Copy the total confirmed and deceased case numbers to HGAC_COVID_19_US_MSAs_Confirmed_and_Deceased_Cases
    print("            Houston_Total_Confirmed")
    arcpy.CalculateField_management('table_tv', "Houston_Total_Confirmed", str(total_confirmed))

    print("            Houston_Total_Deceased")
    arcpy.CalculateField_management('table_tv', "Houston_Total_Deceased", str(total_deceased))

    # Compose date query of the day before the iterated date
    previous_day = day - datetime.timedelta(1)
    previous_day_query = earcpy.compose_single_date_query(table, "Date_", previous_day, "=")

    # Calculate changes in cases
    print("            Houston_Confirmed_Change")
    confirmed_change = earcpy.calculate_difference(table, "Houston_Total_Confirmed", this_day_query, previous_day_query)
    arcpy.CalculateField_management('table_tv', "Houston_Confirmed_Change", str(confirmed_change))

    print("            Houston_Total_Deceased")
    deceased_change = earcpy.calculate_difference(table, "Houston_Total_Deceased", this_day_query, previous_day_query)
    arcpy.CalculateField_management('table_tv', "Houston_Deceased_Change", str(deceased_change))

    # Compose date query of the 7-day period from 6 days before the iterated date to the iterated date
    past_week_query = earcpy.compose_double_date_query(table, "Date_", end_day=day, period=7)

    # Calculate 7-day average changes in cases
    print("            Houston_Confirmed_Mov_Avg")
    confirmed_change_list = earcpy.list_values(table, "Houston_Confirmed_Change", past_week_query)
    confirmed_moving_average = float(sum(confirmed_change_list)) / len(confirmed_change_list)
    arcpy.CalculateField_management('table_tv', "Houston_Confirmed_Mov_Avg", str(confirmed_moving_average))

    print("            Houston_Deceased_Mov_Avg")
    deceased_change_list = earcpy.list_values(table, "Houston_Deceased_Change", past_week_query)
    deceased_moving_average = float(sum(deceased_change_list)) / len(deceased_change_list)
    arcpy.CalculateField_management('table_tv', "Houston_Deceased_Mov_Avg", str(deceased_moving_average))

    # Calculate fatality rate
    print("            Houston_Fatality_Rate")
    arcpy.CalculateField_management('table_tv', "Houston_Fatality_Rate", "100 * [Houston_Total_Deceased] / [Houston_Total_Confirmed]")

def revise_houston_msa_numbers(table, day):
    # Fetch H-GAC counties' confirmed and deceased case numbers from SDE and add up for Houston MSA
    total_confirmed = 0
    total_deceased = 0

    confirmed_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Confirmed_Cases_and_Tests"
    deceased_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Deceased_Cases"

    fields = ["Austin", "Brazoria", "Chambers", "Fort_Bend", "Galveston", "Harris", "Liberty", "Montgomery", "Waller"]
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    cursor = arcpy.da.SearchCursor(confirmed_table, fields, where_clause=this_day_query)
    for row in cursor:
        for i in range(0, 9):
            total_confirmed += row[i]

    cursor = arcpy.da.SearchCursor(deceased_table, fields, where_clause=this_day_query)
    for row in cursor:
        for i in range(0, 9):
            total_deceased += row[i]

    copy_counts(table, day, total_confirmed, total_deceased)

def main():
    workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    this_day_date = raw_input("    Please enter the date intended to revise (m/d/yyyy): ")
    this_day = datetime.datetime.strptime(this_day_date, "%m/%d/%Y")
    order_clause = (None, "ORDER BY Date_")
    
    # Calculate changes in confirmed cases for the day intended to revise and the day before
    print("    HGAC_COVID_19_Confirmed_Cases_and_Tests")
    confirmed_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Confirmed_Cases_and_Tests"

    future_days_query = earcpy.compose_single_date_query(confirmed_table, "Date_", this_day, ">=")
    future_days_cursor = arcpy.da.SearchCursor(confirmed_table, ["Date_"], future_days_query, sql_clause=order_clause)
    for future_days_row in future_days_cursor:
        current_day = future_days_row[0]

        print("        " + str(current_day))
        revise_change(confirmed_table, current_day)
        revise_positivities(confirmed_table, current_day)

    # Reset the value of Positivity_Mov_Avg for the most current day to null
    last_day_query = earcpy.compose_single_date_query(confirmed_table, "Date_", current_day, "=")

    arcpy.MakeTableView_management(confirmed_table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", last_day_query)
    arcpy.CalculateField_management('table_tv', "Positivity_Mov_Avg", "NULL")

    # Calculate changes in active cases for the day intended to revise and the day before
    print("    HGAC_COVID_19_Active_Cases")
    active_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Active_Cases"
    
    future_days_query = earcpy.compose_single_date_query(active_table, "Date_", this_day, ">=")
    future_days_cursor = arcpy.da.SearchCursor(active_table, ["Date_"], future_days_query, sql_clause=order_clause)
    for future_days_row in future_days_cursor:
        current_day = future_days_row[0]

        print("        " + str(current_day))
        revise_change(active_table, current_day)

    # Calculate changes in deceased cases for the day intended to revise and the day before
    print("    HGAC_COVID_19_Deceased_Cases")
    deceased_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Deceased_Cases"
    
    future_days_query = earcpy.compose_single_date_query(deceased_table, "Date_", this_day, ">=")
    future_days_cursor = arcpy.da.SearchCursor(deceased_table, ["Date_"], future_days_query, sql_clause=order_clause)
    for future_days_row in future_days_cursor:
        current_day = future_days_row[0]

        print("        " + str(current_day))
        revise_change(deceased_table, current_day)

    # Calculate changes in recovered cases for the day intended to revise and the day before
    print("    HGAC_COVID_19_Recovered_Cases")
    recovered_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Recovered_Cases"
    
    future_days_query = earcpy.compose_single_date_query(recovered_table, "Date_", this_day, ">=")
    future_days_cursor = arcpy.da.SearchCursor(recovered_table, ["Date_"], future_days_query, sql_clause=order_clause)
    for future_days_row in future_days_cursor:
        current_day = future_days_row[0]

        print("        " + str(current_day))
        revise_change(recovered_table, current_day)

    # Copy changes to the national table
    print("    HGAC_COVID_19_US_MSAs_Confirmed_and_Deceased_Cases")
    msa_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_US_MSAs_Confirmed_and_Deceased_Cases"

    future_days_query = earcpy.compose_single_date_query(msa_table, "Date_", this_day, ">=")
    future_days_cursor = arcpy.da.SearchCursor(deceased_table, ["Date_"], future_days_query, sql_clause=order_clause)
    for future_days_row in future_days_cursor:
        current_day = future_days_row[0]

        print("        " + str(current_day))
        revise_houston_msa_numbers(msa_table, current_day)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Revise COVID-19 Numbers tool ...")
    print("Version 1.2")
    print("Last update: 2/24/2021")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

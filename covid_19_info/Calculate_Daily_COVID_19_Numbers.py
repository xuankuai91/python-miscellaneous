import arcpy, datetime, sys
sys.path.append(r'\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Process Automation\Modules\Bin')
import earcpy

def calculate_change(table, day):
    # Calculate total number of cases
    print("                Total")
    # Compose date query of the day intended to revise
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    arcpy.CalculateField_management(table, "Total", "[Austin] + [Brazoria] + [Chambers] + [Colorado] + [Fort_Bend] + [Galveston] + [Harris] + [Liberty] + [Matagorda] + [Montgomery] + [Walker] + [Waller] + [Wharton]")

    print("                Change")
    # Compose date query of the previous day before the day intended to revise
    previous_day = day - datetime.timedelta(1)
    previous_day_query = earcpy.compose_single_date_query(table, "Date_", previous_day, "=")

    # Calculate change in case
    change = earcpy.calculate_difference(table, "Total", this_day_query, previous_day_query)

    arcpy.CalculateField_management('table_tv', "Change", str(change))

    print("                Mov_Avg")

    # Compose date query of the 7-day period from a week before the execution date to the previous day of the execution date
    past_week_query = earcpy.compose_double_date_query(table, "Date_", end_day=day, period=7)

    # Calculate 7-day average change in cases
    change_list = earcpy.list_values(table, "Change", past_week_query)
    moving_average = float(sum(change_list)) / len(change_list)

    arcpy.CalculateField_management('table_tv', "Mov_Avg", str(moving_average))

def calculate_positivities(table, day):
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

def main():
    arcpy.env.workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.overwriteOutput = True

    print("    Revising COVID-19 case data ...")
    this_day_date = raw_input("Please enter the day intended to revise (m/d/yyyy): ")
    this_day = datetime.datetime.strptime(this_day_date, "%m/%d/%Y")
    order_clause = (None, "ORDER BY Date_")
    
    # Calculate changes in confirmed cases for the day intended to revise and the day before
    print("        HGAC_COVID_19_Confirmed_Cases_and_Tests")
    confirmed_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Confirmed_Cases_and_Tests"

    future_days_query = earcpy.compose_single_date_query(confirmed_table, "Date_", this_day, ">=")
    future_days_cursor = arcpy.da.SearchCursor(confirmed_table, ["Date_", "Total", "Change", "Mov_Avg"], future_days_query, sql_clause=order_clause)
    for future_days_row in future_days_cursor:
        current_day = future_days_row[0]
        print("            " + str(current_day))

        calculate_change(confirmed_table, current_day)
        calculate_positivities(confirmed_table, current_day)

    # Calculate changes in active cases for the day intended to revise and the day before
    print("        HGAC_COVID_19_Active_Cases")
    active_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Active_Cases"
    
    future_days_query = earcpy.compose_single_date_query(active_table, "Date_", this_day, ">=")
    future_days_cursor = arcpy.da.SearchCursor(active_table, ["Date_", "Total", "Change", "Mov_Avg"], future_days_query, sql_clause=order_clause)
    for future_days_row in future_days_cursor:
        current_day = future_days_row[0]
        print("            " + str(current_day))

        calculate_change(active_table, current_day)

    # Calculate changes in deceased cases for the day intended to revise and the day before
    print("        HGAC_COVID_19_Deceased_Cases")
    deceased_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Deceased_Cases"
    
    future_days_query = earcpy.compose_single_date_query(deceased_table, "Date_", this_day, ">=")
    future_days_cursor = arcpy.da.SearchCursor(deceased_table, ["Date_", "Total", "Change", "Mov_Avg"], future_days_query, sql_clause=order_clause)
    for future_days_row in future_days_cursor:
        current_day = future_days_row[0]
        print("            " + str(current_day))

        calculate_change(deceased_table, current_day)

    # Calculate changes in recovered cases for the day intended to revise and the day before
    print("        HGAC_COVID_19_Recovered_Cases")
    recovered_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Recovered_Cases"
    
    future_days_query = earcpy.compose_single_date_query(recovered_table, "Date_", this_day, ">=")
    future_days_cursor = arcpy.da.SearchCursor(recovered_table, ["Date_", "Total", "Change", "Mov_Avg"], future_days_query, sql_clause=order_clause)
    for future_days_row in future_days_cursor:
        current_day = future_days_row[0]
        print("            " + str(current_day))

        calculate_change(recovered_table, current_day)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Revise COVID-19 Numbers tool")
    print("Version 1.1")
    print("Last update: 10/20/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

import arcpy, datetime, sys
sys.path.append(r'\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Process Automation\Modules\Bin')
import earcpy

def revise_change(table, field, day):
    # Compose date query of the day intended to revise
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)
    arcpy.CalculateField_management('table_tv', "Fatality_Rate", "100 * [Deceased] / [Confirmed]")

    print("                Change")

    # Compose date query of the previous day intended to revise
    previous_day = day - datetime.timedelta(1)
    previous_day_query = earcpy.compose_single_date_query(table, "Date_", previous_day, "=")

    # Calculate change in case
    change = earcpy.calculate_difference(table, field, this_day_query, previous_day_query)

    arcpy.CalculateField_management('table_tv', field + "_Change", str(change))

    print("                Mov_Avg")
    # Compose date query of the 7-day period from a week before the execution date to the previous day of the execution date
    past_week_query = earcpy.compose_double_date_query(table, "Date_", end_day=day, period=7)

    # Calculate 7-day average change in cases
    change_list = earcpy.list_values(table, field + "_Change", past_week_query)
    moving_average = float(sum(change_list)) / len(change_list)

    arcpy.CalculateField_management('table_tv', field + "_Mov_Avg", str(moving_average))

def revise_positivities(table, day):
    print("            Positivity")
    # Compose date query of the day before the execution date (for the latest cases data)
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)
    arcpy.CalculateField_management('table_tv', "Positivity", "100 * [Confirmed] / [Tests]")

    print("            Positivity_Mov_Avg")
    # Compose date query of the previous day before the day intended to revise
    previous_day = day - datetime.timedelta(1)
    previous_day_query = earcpy.compose_single_date_query(table, "Date_", previous_day, "=")

    # Calculate change in test
    change = earcpy.calculate_difference(table, "Tests", this_day_query, previous_day_query)
    arcpy.CalculateField_management('table_tv', "Tests_Change", str(change))

    # Compose date query of the 7-day period from 1 week before the previous day of the execution date to two days before the execution date
    past_week_query = earcpy.compose_double_date_query(table, "Date_", end_day=day, period=7)

    confirmed_change_list = earcpy.list_values(table, "Confirmed_Change", past_week_query)
    tests_change_list = earcpy.list_values(table, "Tests_Change", past_week_query)

    positivity_moving_average = 100 * float(sum(confirmed_change_list)) / sum(tests_change_list)
    arcpy.CalculateField_management('table_tv', "Positivity_Mov_Avg", str(positivity_moving_average))

def main():
    workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    this_day_date = raw_input("    Please enter the date intended to revise (m/d/yyyy): ")
    this_day = datetime.datetime.strptime(this_day_date, "%m/%d/%Y")
    order_clause = (None, "ORDER BY Date_")
    
    # Calculate changes in  cases for the day intended to revise and the day before
    print("    HGAC_COVID_19_Harris_County_Info")
    table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Harris_County_Info"

    future_days_query = earcpy.compose_single_date_query(table, "Date_", this_day, ">=")
    future_days_cursor = arcpy.da.SearchCursor(table, ["Date_"], future_days_query, sql_clause=order_clause)
    for future_days_row in future_days_cursor:
        current_day = future_days_row[0]

        print("        " + str(current_day))
        for field in ["Confirmed", "Active", "Deceased", "Recovered"]:
            print("            " + field)
            revise_change(table, field, current_day)

        revise_positivities(table, current_day)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Revise Harris County COVID-19 Numbers tool ...")
    print("Version 1.0")
    print("Last update: 2/16/2022")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

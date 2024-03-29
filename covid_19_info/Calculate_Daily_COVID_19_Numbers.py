import arcpy, datetime, sys, urllib, json
sys.path.append(r'\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Process Automation\Modules\Bin')
import earcpy

def fetch_fbcph_case_counts(table, date):
    print("            Fort Bend")
    query = "{} = 'Fort Bend'".format(arcpy.AddFieldDelimiters(table, "NAME"))
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch case data from DSHS
    url = "https://services6.arcgis.com/Lpf5uekGKCMMIEUK/ArcGIS/rest/services/Cases_current/FeatureServer/0/query?where=1%3D1&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token="
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    cases = data["features"][0]["attributes"]["confirmed"]
    fatalities = data["features"][0]["attributes"]["deaths"]

    arcpy.CalculateField_management('table_tv', "No_of_Cases", str(cases))
    arcpy.CalculateField_management('table_tv', "No_of_Deaths", str(fatalities))

    arcpy.CalculateField_management('table_tv', "Last_Updated", date)

def copy_case_counts(table, fields, county_summary, day):
    try:
        # Insert a new row to table
        target_cursor = arcpy.InsertCursor(table)
        target_row = target_cursor.newRow()

        # Write date of the day before the execution date
        date = "{}/{}/{}".format(day.year, day.month, day.day)
        target_row.setValue("Date_", date)
        target_cursor.insertRow(target_row)

    except:
        pass

    # Compose date query of the day before the execution date (for the latest cases data)
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    # Copy case count from HGAC_Counties_COVID_19_Cases to table
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    county_cursor = arcpy.da.SearchCursor(county_summary, fields)

    for county_row in county_cursor:
        county_name = county_row[0]
        value = county_row[1]

        if county_name == "Fort Bend":
            county_name = "Fort_Bend"

        print("        " + county_name)
        arcpy.CalculateField_management('table_tv', county_name, str(value))
    

def calculate_change(table, day):
    # Calculate total number of cases
    print("        Total")
    arcpy.CalculateField_management(table, "Total", "[Austin] + [Brazoria] + [Chambers] + [Colorado] + [Fort_Bend] + [Galveston] + [Harris] + [Liberty] + [Matagorda] + [Montgomery] + [Walker] + [Waller] + [Wharton]")

    print("        Change")

    # Compose date query of the day before the execution date (for the latest cases data)
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    # Compose date query of two days before the execution date (for the previous cases data)
    previous_day = day - datetime.timedelta(1)
    previous_day_query = earcpy.compose_single_date_query(table, "Date_", previous_day, "=")

    # Calculate change in cases
    change = earcpy.calculate_difference(table, "Total", this_day_query, previous_day_query)

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    arcpy.CalculateField_management('table_tv', "Change", str(change))
    
    print("        Mov_Avg")

    # Compose date query of the 7-day period from a week before the execution date to the previous day of the execution date
    past_week_query = earcpy.compose_double_date_query(table, "Date_", end_day=day, period=7)

    # Calculate 7-day average change in cases
    change_list = earcpy.list_values(table, "Change", past_week_query)
    moving_average = float(sum(change_list)) / len(change_list)

    arcpy.CalculateField_management('table_tv', "Mov_Avg", str(moving_average))

def fetch_test_counts(table, county):
    print("            " + county)
    query = "{} = '{}'".format(arcpy.AddFieldDelimiters(table, "NAME"), county)
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Convert "Fort Bend" to "Fort+Bend" to fit URL format
    if county == "Fort Bend":
        county = "Fort+Bend"

    # Fetch test data from DSHS
    url = "https://services3.arcgis.com/vljlarU2635mITsl/ArcGIS/rest/services/covid19_test_data_hosted/FeatureServer/0/query?where=county%3D%27{}%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token=".format(county)
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    tests = data["features"][0]["attributes"]["total_tests"]
    arcpy.CalculateField_management('table_tv', "No_of_Tests", str(tests))

def calculate_test_count(table, county_summary, day):
    print("        Tests")
    county_cursor = arcpy.da.SearchCursor(county_summary, ["No_of_Tests"])

    test_list = [county_row[0] for county_row in county_cursor]
    total_tests = sum(test_list)

    # Compose date query of two days before the execution date (for the previous cases data)
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    arcpy.CalculateField_management('table_tv', "Tests", str(total_tests))

def calculate_positivities(table, county_summary, day):
    print("        Positivity")
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)
    arcpy.CalculateField_management('table_tv', "Positivity", "100 * [Total] / [Tests]")

    print("        Positivity_Mov_Avg")
    # Compose date query of the day before the execution date (for the latest cases data)
    previous_day = day - datetime.timedelta(1)
    previous_day_query = earcpy.compose_single_date_query(table, "Date_", previous_day, "=")

    tests_change = earcpy.calculate_difference(table, "Tests", this_day_query, previous_day_query)

    arcpy.CalculateField_management('table_tv', "Tests_Change", str(tests_change))

    # Compose date query of the 7-day period from 1 week before the previous day of the execution date to two days before the execution date
    past_week_query = earcpy.compose_double_date_query(table, "Date_", end_day=day, period=7)

    # Calculate 7-day average positivity rate
    confirmed_change_list = earcpy.list_values(table, "Change", past_week_query)
    tests_change_list = earcpy.list_values(table, "Tests_Change", past_week_query)

    positivity_moving_average = 100 * float(sum(confirmed_change_list)) / sum(tests_change_list)
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)
    arcpy.CalculateField_management('table_tv', "Positivity_Mov_Avg", str(positivity_moving_average))

def calculate_table(table, fields, county_summary, day):
    copy_case_counts(table, fields, county_summary, day)
    calculate_change(table, day)

def main():
    workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    yesterday = datetime.datetime.today() - datetime.timedelta(1)

    print("    HGAC_Counties_COVID_19_Cases")
    county_summary = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Info\Global.GLOBAL_ADMIN.HGAC_Counties_COVID_19_Cases"

    if yesterday.strftime('%w') in ("0", "1", "2", "3", "4"): # Update Fort Bend County cases on weekdays only
        print("        No_of_Cases, No_of_Deaths")
        yesterday_date = "{}/{}/{}".format(yesterday.year, yesterday.month, yesterday.day)
        fetch_fbcph_case_counts(county_summary, "CDate(#{}#)".format(yesterday_date))

    # Fetch test counts for the previous day
    print("        No_of_Tests")
    counties = ["Austin", "Brazoria", "Chambers", "Colorado", "Fort Bend", "Galveston", "Harris", "Liberty", "Matagorda", "Montgomery", "Walker", "Waller", "Wharton"]
    for county in counties:
        fetch_test_counts(county_summary, county)

    print("        Positivity")
    arcpy.CalculateField_management(county_summary, "Positivity", "100 * [No_of_Cases] / [No_of_Tests]") # Calculate total positivity

    # Copy data from HGAC_Counties_COVID_19_Cases to HGAC_COVID_19_Confirmed_Cases_and_Tests, and calculate total, change, and 7-day average
    print("    HGAC_COVID_19_Confirmed_Cases_and_Tests")
    confirmed_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Confirmed_Cases_and_Tests"
    calculate_table(confirmed_table, ["NAME", "No_of_Cases"], county_summary, yesterday)
    calculate_test_count(confirmed_table, county_summary, yesterday)
    calculate_positivities(confirmed_table, county_summary, yesterday)

    # Copy data from HGAC_Counties_COVID_19_Cases to HGAC_COVID_19_Deceased_Cases, and calculate total, change, and 7-day average
    print("    HGAC_COVID_19_Deceased_Cases")
    deceased_table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Deceased_Cases"
    calculate_table(deceased_table, ["NAME", "No_of_Deaths"], county_summary, yesterday)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Calculate Daily COVID-19 Numbers tool ...")
    print("Version 1.9")
    print("Last update: 2/16/2022")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

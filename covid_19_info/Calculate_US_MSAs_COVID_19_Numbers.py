import arcpy, datetime, urllib, json
sys.path.append(r'\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Process Automation\Modules\Bin')
import earcpy

def fetch_jhu_numbers(county, state):
    # Fetch confirmed and deceased case numbers from JHU by county and add up by MSA
    url = "https://services9.arcgis.com/6Hv9AANartyT7fJW/ArcGIS/rest/services/USCounties_cases_V1/FeatureServer/0/query?where=Countyname%3D%27{}%27+AND+ST_Name%3D%27{}%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token=".format(county, state)
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    confirmed = data["features"][0]["attributes"]["Confirmed"]
    deceased = data["features"][0]["attributes"]["Deaths"]

    return confirmed, deceased

def copy_counts(table, day, msa, total_confirmed, total_deceased):
    # Compose date query of the day before the execution date (for the latest cases data)
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    # Copy the total confirmed and deceased case numbers to HGAC_COVID_19_US_MSAs_Confirmed_and_Deceased_Cases
    print("        Confirmed")
    arcpy.CalculateField_management('table_tv', msa + "_Total_Confirmed", str(total_confirmed))

    print("        Deceased")
    arcpy.CalculateField_management('table_tv', msa + "_Total_Deceased", str(total_deceased))

def import_atlanta_numbers(table, day):
    print("    Importing Atlanta MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy Georgia counties' numbers
    print("        Georgia")
    counties = ["Barrow", "Bartow", "Butts", "Carroll", "Cherokee", "Clayton", "Cobb", "Coweta", "Dawson", "DeKalb", "Douglas", "Fayette", "Forsyth", "Fulton", "Gwinnett", "Haralson", "Heard", "Henry", "Jasper", "Lamar", "Meriwether", "Morgan", "Newton", "Paulding", "Pickens", "Pike", "Rockdale", "Spalding", "Walton"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Georgia")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Atlanta", total_confirmed, total_deceased)

def import_baltimore_numbers(table, day):
    print("    Importing Baltimore MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy Maryland counties' numbers
    print("        Maryland")
    counties = ["Anne Arundel", "Baltimore", "Baltimore City", "Carroll", "Harford", "Howard", "Queen Anne''s"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Maryland")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Baltimore", total_confirmed, total_deceased)

def import_chicago_numbers(table, day):
    print("    Importing Chicago MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy Illinois counties' numbers
    print("        Illinois")
    counties = ["Cook", "DeKalb", "DuPage", "Grundy", "Kane", "Kankakee", "Kendall", "Lake", "McHenry", "Will"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Illinois")
        
        total_confirmed += confirmed
        total_deceased += deceased

    # Copy Indiana counties' numbers
    print("        Indiana")
    counties = ["Jasper", "Lake", "Newton", "Porter"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Indiana")
        
        total_confirmed += confirmed
        total_deceased += deceased

    # Copy Kenosha County, Wisconsin counties' numbers
    print("        Wisconsin")
    print("            Kenosha")
    confirmed, deceased = fetch_jhu_numbers("Kenosha", "Wisconsin")
        
    total_confirmed += confirmed
    total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Chicago", total_confirmed, total_deceased)

def import_cincinnati_numbers(table, day):
    print("    Importing Cincinnati MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy Indiana counties' numbers
    print("        Indiana")
    counties = ["Dearborn", "Franklin", "Ohio"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Indiana")
        
        total_confirmed += confirmed
        total_deceased += deceased

    
    # Copy Kentucky counties' numbers
    print("        Kentucky")
    counties = ["Boone", "Bracken", "Campbell", "Gallatin", "Grant", "Kenton", "Pendleton"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Kentucky")
        
        total_confirmed += confirmed
        total_deceased += deceased

    # Copy Ohio counties' numbers
    print("        Ohio")
    counties = ["Brown", "Butler", "Clermont", "Hamilton", "Warren"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Ohio")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Cincinnati", total_confirmed, total_deceased)

def import_cleveland_numbers(table, day):
    print("    Importing Cleveland MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy Ohio counties' numbers
    print("        Ohio")
    counties = ["Carroll", "Cuyahoga", "Geauga", "Lake", "Lorain", "Medina", "Portage", "Stark", "Summit"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Ohio")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Cleveland", total_confirmed, total_deceased)

def import_dallas_numbers(table, day):
    print("    Importing Dallas MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy Texas counties' numbers
    print("        Texas")
    counties = ["Collin", "Dallas", "Denton", "Ellis", "Hunt", "Johnson", "Kaufman", "Parker", "Rockwall", "Tarrant", "Wise"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Texas")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Dallas", total_confirmed, total_deceased)


def import_houston_numbers(table, day):
    # Fetch H-GAC counties' confirmed and deceased case numbers from SDE and add up for Houston MSA
    print("    Importing Houston MSA numbers ...")
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

    print("    Copying counts ...")
    copy_counts(table, day, "Houston", total_confirmed, total_deceased)

def import_miami_numbers(table, day):
    print("    Importing Miami MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy Florida counties' numbers
    print("        Florida")
    counties = ["Broward", "Miami-Dade", "Palm Beach"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Florida")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Miami", total_confirmed, total_deceased)

def import_orlando_numbers(table, day):
    print("    Importing Orlando MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy Florida counties' numbers
    print("        Florida")
    counties = ["Lake", "Orange", "Osceola", "Seminole"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Florida")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Orlando", total_confirmed, total_deceased)

def import_raleigh_numbers(table, day):
    print("    Importing Raleigh MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy North Carolina counties' numbers
    print("        North Carolina")
    counties = ["Chatham", "Durham", "Franklin", "Granville", "Johnston", "Orange", "Person", "Wake"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "North Carolina")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Raleigh", total_confirmed, total_deceased)

def import_san_diego_numbers(table, day):
    print("    Importing San Diego MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy California counties' numbers
    print("        California")
    print("            San Diego")
    confirmed, deceased = fetch_jhu_numbers("San Diego", "California")
    
    total_confirmed += confirmed
    total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "San_Diego", total_confirmed, total_deceased)

def import_san_jose_numbers(table, day):
    print("    Importing San Jose MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy California counties' numbers
    print("        California")
    counties = ["San Benito", "Santa Clara"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "California")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "San_Jose", total_confirmed, total_deceased)

def import_seattle_numbers(table, day):
    print("    Importing Seattle MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy Washington counties' numbers
    print("        Washington")
    counties = ["King", "Pierce", "Snohomish"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Washington")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Seattle", total_confirmed, total_deceased)

def import_tampa_numbers(table, day):
    print("    Importing Tampa MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy Florida counties' numbers
    print("        Florida")
    counties = ["Hernando", "Hillsborough", "Pasco", "Pinellas"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Florida")
        
        total_confirmed += confirmed
        total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Tampa", total_confirmed, total_deceased)

def import_washington_numbers(table, day):
    print("    Importing Washington MSA numbers ...")
    total_confirmed = 0
    total_deceased = 0

    # Copy District of Columbia counties' numbers
    print("        District of Columbia")
    confirmed, deceased = fetch_jhu_numbers("District of Columbia", "District of Columbia")
        
    total_confirmed += confirmed
    total_deceased += deceased

    # Copy Maryland counties' numbers
    print("        Maryland")
    counties = ["Calvert", "Charles", "Frederick", "Montgomery", "Prince George''s"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Maryland")
        
        total_confirmed += confirmed
        total_deceased += deceased

    
    # Copy Virginia counties' numbers
    print("        Virginia")
    counties = ["Arlington", "Clarke", "Culpeper", "Fairfax", "Fauquier", "Loudoun", "Prince William", "Rappahannock", "Spotsylvania", "Stafford"]
    for county in counties:
        print("            " + county)
        confirmed, deceased = fetch_jhu_numbers(county, "Virginia")
        
        total_confirmed += confirmed
        total_deceased += deceased

    # Copy Jefferson County, West Virginia numbers
    print("        West Virginia")
    print("            Jefferson")
    confirmed, deceased = fetch_jhu_numbers("Jefferson", "West Virginia")
    
    total_confirmed += confirmed
    total_deceased += deceased

    print("    Copying counts ...")
    copy_counts(table, day, "Washington", total_confirmed, total_deceased)

def calculate_stats(table, day):
    print("    Calculating case changes ...")
    # Compose date query of the day before the execution date (for the latest cases data)
    this_day_query = earcpy.compose_single_date_query(table, "Date_", day, "=")

    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", this_day_query)

    # Compose date query of two days before the execution date (for the previous cases data)
    previous_day = day - datetime.timedelta(1)
    previous_day_query = earcpy.compose_single_date_query(table, "Date_", previous_day, "=")

    # Compose date query of the 7-day period from 1 week before the previous day of the execution date to two days before the execution date
    past_week_query = earcpy.compose_double_date_query(table, "Date_", end_day=day, period=7)

    msas = ["Atlanta", "Baltimore", "Chicago", "Cincinnati", "Cleveland", "Dallas", "Houston", "Miami", "Orlando", "Raleigh", "San_Diego", "San_Jose", "Seattle", "Tampa", "Washington"]
    for msa in msas:
        print("        " + msa)

        # Calculate changes in cases
        print("            Confirmed")
        confirmed_change = earcpy.calculate_difference(table, msa + "_Total_Confirmed", this_day_query, previous_day_query)
        arcpy.CalculateField_management('table_tv', msa + "_Confirmed_Change", str(confirmed_change))

        print("            Deceased")
        deceased_change = earcpy.calculate_difference(table, msa + "_Total_Deceased", this_day_query, previous_day_query)
        arcpy.CalculateField_management('table_tv', msa + "_Deceased_Change", str(deceased_change))

        # Calculate 7-day average changes in cases
        confirmed_change_list = earcpy.list_values(table, msa + "_Confirmed_Change", past_week_query)
        confirmed_moving_average = float(sum(confirmed_change_list)) / len(confirmed_change_list)
        arcpy.CalculateField_management('table_tv', msa + "_Confirmed_Mov_Avg", str(confirmed_moving_average))

        deceased_change_list = earcpy.list_values(table, msa + "_Deceased_Change", past_week_query)
        deceased_moving_average = float(sum(deceased_change_list)) / len(deceased_change_list)
        arcpy.CalculateField_management('table_tv', msa + "_Deceased_Mov_Avg", str(deceased_moving_average))

        # Calculate fatality rate
        print("            Fatality rate")
        arcpy.CalculateField_management('table_tv', msa + "_Fatality_Rate", "100 * [{}_Total_Deceased] / [{}_Total_Confirmed]".format(msa, msa))

def main():
    workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    yesterday = datetime.datetime.today() - datetime.timedelta(1)
    table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_US_MSAs_Confirmed_and_Deceased_Cases"

    try:
        # Insert a new row to table
        target_cursor = arcpy.InsertCursor(table)
        target_row = target_cursor.newRow()

        # Write date of the day before the execution date
        date = "{}/{}/{}".format(yesterday.year, yesterday.month, yesterday.day)
        target_row.setValue("Date_", date)
        target_cursor.insertRow(target_row)

    except:
        pass

    # Import confirmed and deceased case numbers of the counties in each MSA and calculate the sums
    import_atlanta_numbers(table, yesterday)
    import_baltimore_numbers(table, yesterday)
    import_chicago_numbers(table, yesterday)
    import_cincinnati_numbers(table, yesterday)
    import_cleveland_numbers(table, yesterday)
    import_dallas_numbers(table, yesterday)
    import_houston_numbers(table, yesterday)
    import_miami_numbers(table, yesterday)
    import_orlando_numbers(table, yesterday)
    import_raleigh_numbers(table, yesterday)
    import_san_diego_numbers(table, yesterday)
    import_san_jose_numbers(table, yesterday)
    import_seattle_numbers(table, yesterday)
    import_tampa_numbers(table, yesterday)
    import_washington_numbers(table, yesterday)

    # Calculate daily changes in cases, 7-day moving averages, and fatality rates of each MSA
    calculate_stats(table, yesterday)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Calculate US MSAs COVID-19 Numbers tool")
    print("Version 1.0")
    print("Last update: 1/21/2021")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

import arcpy, datetime, urllib, json

def fetch_dshs_case_counts(table, county, date):
    print("            " + county)
    query = "{} = '{}'".format(arcpy.AddFieldDelimiters(table, "NAME"), county)
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch case data from DSHS
    url = "https://services5.arcgis.com/ACaLB9ifngzawspq/ArcGIS/rest/services/TX_DSHS_COVID19_Cases_Service/FeatureServer/1/query?where=County%3D%27{}%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token=".format(county)
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    actives = data["features"][0]["attributes"]["Active"]
    fatalities = data["features"][0]["attributes"]["Fatalities"]
    recoveries = data["features"][0]["attributes"]["Recoveries"]
    cases = actives + fatalities + recoveries

    if county == "Waller": # Update number of deaths only for Waller County
        cases = data["features"][0]["attributes"]["Positive"]
        actives = data["features"][0]["attributes"]["Active"]
        fatalities = data["features"][0]["attributes"]["Fatalities"]
        recoveries = cases - actives - fatalities
    else:
        actives = data["features"][0]["attributes"]["Active"]
        fatalities = data["features"][0]["attributes"]["Fatalities"]
        recoveries = data["features"][0]["attributes"]["Recoveries"]
        cases = actives + fatalities + recoveries
    
    arcpy.CalculateField_management('table_tv', "No_of_Cases", str(cases))
    arcpy.CalculateField_management('table_tv', "No_of_Actives", str(actives))
    arcpy.CalculateField_management('table_tv', "No_of_Deaths", str(fatalities))
    arcpy.CalculateField_management('table_tv', "No_of_Recoveries", str(recoveries))

    arcpy.CalculateField_management('table_tv', "Last_Updated", "CDate(#{}#)".format(date))

def fetch_hcph_case_counts(table, day, date):
    print("            Harris")
    query = "{} = 'Harris'".format(arcpy.AddFieldDelimiters(table, "NAME"))
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch case data from DSHS
    url = "https://services.arcgis.com/su8ic9KbA7PYVxPS/ArcGIS/rest/services/HCPHCovidDashboard/FeatureServer/1/query?where=Source%3D%27Combined%27+AND+DATE%3DTIMESTAMP+%27{}%2F{}%2F{}+6%3A00%3A00+AM%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token=".format(day.month, day.day, day.year)
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    actives = data["features"][0]["attributes"]["Active"]
    fatalities = data["features"][0]["attributes"]["Deceased"]
    recoveries = data["features"][0]["attributes"]["Recovered"]
    cases = actives + fatalities + recoveries

    arcpy.CalculateField_management('table_tv', "No_of_Cases", str(cases))
    arcpy.CalculateField_management('table_tv', "No_of_Actives", str(actives))
    arcpy.CalculateField_management('table_tv', "No_of_Deaths", str(fatalities))
    arcpy.CalculateField_management('table_tv', "No_of_Recoveries", str(recoveries))

    arcpy.CalculateField_management('table_tv', "Last_Updated", "CDate(#{}#)".format(date))

def fetch_ccph_case_counts(table, date):
    print("            Chambers")
    query = "{} = 'Chambers'".format(arcpy.AddFieldDelimiters(table, "NAME"))
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch case data from DSHS
    url = "https://services8.arcgis.com/5rne9bHBCbjGEtW8/ArcGIS/rest/services/Chambers_Case_Count/FeatureServer/0/query?where=1%3D1&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token="
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    cases = data["features"][0]["attributes"]["ConfirmedCases"]
    fatalities = data["features"][0]["attributes"]["TotalDeaths"]
    recoveries = data["features"][0]["attributes"]["TotalRecovered"]
    actives = cases - fatalities - recoveries

    arcpy.CalculateField_management('table_tv', "No_of_Cases", str(cases))
    arcpy.CalculateField_management('table_tv', "No_of_Actives", str(actives))
    arcpy.CalculateField_management('table_tv', "No_of_Deaths", str(fatalities))
    arcpy.CalculateField_management('table_tv', "No_of_Recoveries", str(recoveries))

def fetch_mcph_case_counts(table, date):
    print("            Montgomery")
    query = "{} = 'Montgomery'".format(arcpy.AddFieldDelimiters(table, "NAME"))
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch case data from DSHS
    url = "https://services1.arcgis.com/PRoAPGnMSUqvTrzq/ArcGIS/rest/services/CoronavirusCases_current/FeatureServer/0/query?where=Name%3D%27Montgomery+County%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token="
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    cases = data["features"][0]["attributes"]["positive"]
    fatalities = data["features"][0]["attributes"]["deaths"]
    recoveries = data["features"][0]["attributes"]["recovered"]
    actives = cases - fatalities - recoveries

    arcpy.CalculateField_management('table_tv', "No_of_Cases", str(cases))
    arcpy.CalculateField_management('table_tv', "No_of_Actives", str(actives))
    arcpy.CalculateField_management('table_tv', "No_of_Deaths", str(fatalities))
    arcpy.CalculateField_management('table_tv', "No_of_Recoveries", str(recoveries))

    arcpy.CalculateField_management('table_tv', "Last_Updated", "CDate(#{}#)".format(date))

def fetch_test_counts(table, county):
    print("            " + county)
    query = "{} = '{}'".format(arcpy.AddFieldDelimiters(table, "NAME"), county)
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Convert "Fort Bend" to "Fort+Bend" to fit URL format
    if county == "Fort Bend":
        county = "Fort+Bend"

    # Fetch test data from DSHS
    url = "https://services5.arcgis.com/ACaLB9ifngzawspq/ArcGIS/rest/services/TX_DSHS_COVID19_TestData_Service/FeatureServer/0/query?where=County%3D%27{}%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token=".format(county)
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    tests = data["features"][0]["attributes"]["Cumulative"]
    arcpy.CalculateField_management('table_tv', "No_of_Tests", str(tests))

def main():
    workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    day = datetime.datetime.today()
    date = "{}/{}/{}".format(day.year, day.month, day.day)

    table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Info\Global.GLOBAL_ADMIN.HGAC_Counties_COVID_19_Cases"

    print("    HGAC_Counties_COVID_19_Cases")
    print("        No_of_Cases, No_of_Actives, No_of_Deaths, No_of_Recoveries")
    for county in ["Austin", "Matagorda", "Waller"]:
        fetch_dshs_case_counts(table, county, date)

    fetch_hcph_case_counts(table, day, date)

    if day.strftime('%w') in ("1", "2", "3", "4", "5"): # Update Chambers County and Montgomery County cases on weekdays only
        fetch_ccph_case_counts(table, date)
        fetch_mcph_case_counts(table, date)

    print("        No_of_Tests")
    counties = ["Austin", "Brazoria", "Chambers", "Colorado", "Fort Bend", "Galveston", "Harris", "Liberty", "Matagorda", "Montgomery", "Walker", "Waller", "Wharton"]

    for county in counties:
        fetch_test_counts(table, county)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Fetch Daily COVID-19 Numbers tool ...")
    print("Version 1.0")
    print("Last update: 10/20/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

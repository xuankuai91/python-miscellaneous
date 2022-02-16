import arcpy, datetime, urllib, json

def fetch_dshs_case_counts(table, county, day):
    # Offset date discrepancy from DSHS
    pseudo_day = day + datetime.timedelta(1)
    pseudo_date = "{}/{}/{}".format(pseudo_day.year, pseudo_day.month, pseudo_day.day)

    print("            " + county)
    query = "{} = '{}'".format(arcpy.AddFieldDelimiters(table, "NAME"), county)
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch case data from DSHS
    url = "https://services3.arcgis.com/vljlarU2635mITsl/ArcGIS/rest/services/covid19_case_data_hosted/FeatureServer/0/query?where=county%3D%27{}%27+AND+year%3DTIMESTAMP+%27{}+6%3A00%3A00+AM%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token=".format(county, pseudo_date.replace("/", "%2F"))
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    cases = data["features"][0]["attributes"]["confirmed"]
    fatalities = data["features"][0]["attributes"]["fatalities"]
    
    arcpy.CalculateField_management('table_tv', "No_of_Cases", str(cases))
    arcpy.CalculateField_management('table_tv', "No_of_Deaths", str(fatalities))

    date = "{}/{}/{}".format(day.year, day.month, day.day)
    arcpy.CalculateField_management('table_tv', "Last_Updated", "CDate(#{}#)".format(date))

def fetch_hcph_case_counts(table, day, date):
    print("            Harris")
    query = "{} = 'Harris'".format(arcpy.AddFieldDelimiters(table, "NAME"))
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch case data from Harris County
    url = "https://services.arcgis.com/su8ic9KbA7PYVxPS/ArcGIS/rest/services/Download_Current_COVID_Case_Counts/FeatureServer/0/query?where=Source%3D%27All%27&objectIds=&time=&resultType=none&outFields=*&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token="
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    actives = data["features"][0]["attributes"]["Active"]
    fatalities = data["features"][0]["attributes"]["Deaths"]
    recoveries = data["features"][0]["attributes"]["Recovered"]
    cases = actives + fatalities + recoveries

    arcpy.CalculateField_management('table_tv', "No_of_Cases", str(cases))
    arcpy.CalculateField_management('table_tv', "No_of_Deaths", str(fatalities))

    arcpy.CalculateField_management('table_tv', "Last_Updated", "CDate(#{}#)".format(date))

def fetch_ccph_case_counts(table, date):
    print("            Chambers")
    query = "{} = 'Chambers'".format(arcpy.AddFieldDelimiters(table, "NAME"))
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch case data from Chambers County
    url = "https://services8.arcgis.com/5rne9bHBCbjGEtW8/ArcGIS/rest/services/Chambers_Case_Count/FeatureServer/0/query?where=1%3D1&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token="
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    cases = data["features"][0]["attributes"]["ConfirmedCases"]
    fatalities = data["features"][0]["attributes"]["TotalDeaths"]

    arcpy.CalculateField_management('table_tv', "No_of_Cases", str(cases))
    arcpy.CalculateField_management('table_tv', "No_of_Deaths", str(fatalities))

def fetch_mcph_case_counts(table, date):
    print("            Montgomery")
    query = "{} = 'Montgomery'".format(arcpy.AddFieldDelimiters(table, "NAME"))
    arcpy.MakeTableView_management(table, 'table_tv')
    arcpy.SelectLayerByAttribute_management('table_tv', "NEW_SELECTION", query)

    # Fetch case data from Montgomery County
    url = "https://services1.arcgis.com/PRoAPGnMSUqvTrzq/ArcGIS/rest/services/CoronavirusCases_current/FeatureServer/0/query?where=Name%3D%27Montgomery+County%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token="
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    cases = data["features"][0]["attributes"]["positive"]
    fatalities = data["features"][0]["attributes"]["deaths"]

    arcpy.CalculateField_management('table_tv', "No_of_Cases", str(cases))
    arcpy.CalculateField_management('table_tv', "No_of_Deaths", str(fatalities))

    arcpy.CalculateField_management('table_tv', "Last_Updated", "CDate(#{}#)".format(date))

def main():
    workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    day = datetime.datetime.today()
    date = "{}/{}/{}".format(day.year, day.month, day.day)

    table = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_Info\Global.GLOBAL_ADMIN.HGAC_Counties_COVID_19_Cases"

    print("    HGAC_Counties_COVID_19_Cases")
    print("        No_of_Cases, No_of_Deaths")
    for county in ["Austin", "Colorado", "Liberty", "Matagorda", "Walker", "Waller", "Wharton"]:
        fetch_dshs_case_counts(table, county, day)

    fetch_hcph_case_counts(table, day, date)

    if day.strftime('%w') in ("1", "2", "3", "4", "5"): # Update Chambers County cases on weekdays only
        fetch_ccph_case_counts(table, date)

    if day.strftime('%w') == "3": # Update Montgomery County cases on Wednesdays only
        fetch_mcph_case_counts(table, date)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Fetch Daily COVID-19 Numbers tool ...")
    print("Version 1.4")
    print("Last update: 2/16/2022")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

import arcpy, datetime, urllib, json

def main():
    workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    print("    HGAC_COVID_19_TSA_Q_Info")
    day = datetime.datetime.today()
    date = "{}/{}/{}".format(day.year, day.month, day.day)

    # Fetch TSA Q hospitalization data from DSHS
    url = "https://services5.arcgis.com/ACaLB9ifngzawspq/ArcGIS/rest/services/DSHS_COVID_Hospital_Data/FeatureServer/0/query?where=TSA%3D%27Q%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token="
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    total = data["features"][0]["attributes"]["TotalStaff"]
    available = data["features"][0]["attributes"]["AvailHospi"]
    covid_occupied = data["features"][0]["attributes"]["COVIDPatie"]

    tsa_q = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_TSA_Q_Info"

    print("        Inserting new row ...")
    try:
        # Insert a new row to table
        cursor = arcpy.InsertCursor(tsa_q)
        row = cursor.newRow()

        # Write date and fetched values
        row.setValue("Date_", date)
        row.setValue("Total", total)
        row.setValue("Available", available)
        row.setValue("COVID_Occupied", covid_occupied)
        cursor.insertRow(row)

    except:
        pass

    # Calculate derived values
    print("        Total_Occupied")
    arcpy.CalculateField_management(tsa_q, "Total_Occupied", "[Total] - [Available]")

    print("        Occupied_Total_Percentage")
    arcpy.CalculateField_management(tsa_q, "Occupied_Total_Percentage", "100 * [Total_Occupied] / [Total]")

    print("        COVID_Total_Percentage")
    arcpy.CalculateField_management(tsa_q, "COVID_Total_Percentage", "100 * [COVID_Occupied] / [Total]")

    print("        COVID_Occupied_Percentage")
    arcpy.CalculateField_management(tsa_q, "COVID_Occupied_Percentage", "100 * [COVID_Occupied] / [Total_Occupied]")

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Calculate TSA Q Daily COVID-19 Numbers tool ...")
    print("Version 1.2")
    print("Last update: 9/18/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

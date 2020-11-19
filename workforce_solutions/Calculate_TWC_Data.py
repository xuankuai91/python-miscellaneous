import arcpy, datetime

def main():
    arcpy.env.workspace = r"\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Requests\Workforce\UI_Claims"
    arcpy.env.overwriteOutput = True

    # Calculate data for counties
    print("    HGAC_Counties_UI_Claims_TWC")

    county_twc = r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN.HGAC_Workforce_Solutions\Global.GLOBAL_ADMIN.HGAC_Counties_UI_Claims_TWC"
    county_fields = ["UICount", "NAICS1", "NAICSTitle1", "NAICS1Count", "NAICS2", "NAICSTitle2", "NAICS2Count","NAICS3", "NAICSTitle3", "NAICS3Count","NAICS4", "NAICSTitle4", "NAICS4Count","NAICS5", "NAICSTitle5", "NAICS5Count", "Male", "Female", "GenderUnknown", "Week1", "Week2", "Week3", "Week4", "Week5", "BeginDate", "EndDate"]
    arcpy.MakeFeatureLayer_management(county_twc, 'county_twc_layer')
    arcpy.AddJoin_management('county_twc_layer', 'NAME', 'ui_by_county.csv', 'AreaName')

    print("        Copying attributes ...")
    for field in county_fields:
        arcpy.CalculateField_management("county_twc_layer", "Global.GLOBAL_ADMIN.HGAC_Counties_UI_Claims_TWC." + field, "[ui_by_county.csv." + field + "]")
        print("            " + field)

    arcpy.RemoveJoin_management("county_twc_layer")

    # Calculate data for ZIP Code areas
    print("    HGAC_ZIP_Codes_UI_Claims_TWC")

    zip_twc = r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN.HGAC_Workforce_Solutions\Global.GLOBAL_ADMIN.HGAC_ZIP_Codes_UI_Claims_TWC"
    zip_fields = ["UICount", "Male", "Female", "GenderUnknown", "Week1", "Week2", "Week3", "Week4", "Week5", "BeginDate", "EndDate"]
    arcpy.MakeFeatureLayer_management(zip_twc, 'zip_twc_layer')
    arcpy.AddJoin_management('zip_twc_layer', 'Zip_Code', 'ui_by_zipcode.xlsx\ui_by_zipcode$', 'ZIP_CODE')

    print("        Copying attributes ...")
    for field in zip_fields:
        arcpy.CalculateField_management("zip_twc_layer", "Global.GLOBAL_ADMIN.HGAC_ZIP_Codes_UI_Claims_TWC." + field, "[ui_by_zipcode$." + field + "]")
        print("            " + field)

    print("        Filling null values ...")
    arcpy.SelectLayerByAttribute_management("zip_twc_layer", "NEW_SELECTION", '"ui_by_zipcode$.ZIP_CODE" IS NULL')
    arcpy.RemoveJoin_management("zip_twc_layer")

    for field in zip_fields[:9]:
        arcpy.CalculateField_management("zip_twc_layer", field, "0")
        print("            " + field)

    for field in zip_fields[-2:]:
        arcpy.CalculateField_management("zip_twc_layer", field, "NULL")
        print("            " + field)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting HGAC Workforce Solutions UI Claims Data Calculator (TWC Version)")
    print("Version 1.0")
    print("Last update: 7/6/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

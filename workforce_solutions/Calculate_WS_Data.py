import arcpy, datetime

def prepare_claimants_layer():
    print("    Preparing claimants layer ...")
    print("        Correcting addresses ...")
    claimants_temp = "Claimants_" + start_date + "_" + end_date + "_temp"

    arcpy.CalculateField_management(claimants_temp, "Address", "[ShortLabel]")

    print("        Copying feature class to UI_Claimants_" + start_date + "_" + end_date + " ...")
    print("            Creating field map ...")
    field_mappings = arcpy.FieldMappings()

    fields = ["ID", "Address", "City_1", "CountyName", "State_1", "Zip_Code", "Age", "Age_Range", "Gender", "Race", "EducationalAttainment", "Filing_Date", "Industry", "Standard_Occupational_Classification", "Program_Code", "Veteran", "F2_Digit_NAICS", "F2_Digit_NAICS_Title", "F3_Digit_NAICS", "F3_Digit_NAICS_Title", "F4_Digit_NAICS", "F4_Digit_NAICS_Title"]

    for field in fields:
        try:
            field_map = arcpy.FieldMap()
            old_field_name = field

            if field == "City_1":
                new_field_name = "City"
            elif field == "State_1":
                new_field_name = "State"
            elif field == "EducationalAttainment":
                new_field_name = "Education"
            elif field == "Standard_Occupational_Classification":
                new_field_name = "Standard_Occupational_Classific"
            else:
                new_field_name = field

            field_map.addInputField(claimants_temp, old_field_name)

            print("                " + old_field_name + " -> " + new_field_name)
            out_field = field_map.outputField
            out_field.name = new_field_name
            out_field.aliasName = new_field_name
            field_map.outputField = out_field
            field_mappings.addFieldMap(field_map)
        except:
            print("                (" + old_field_name + " does not exist)")
            pass

    print("            Copying feature class ...")
    ui_claimants = "UI_Claimants_" + start_date + "_" + end_date
    arcpy.FeatureClassToFeatureClass_conversion(claimants_temp, r"\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Requests\Workforce\UI_Claims\Default.gdb", ui_claimants, "Status = 'M'", field_mappings)

def spatially_join():
    print("    Spatially joining administrative layers to claimants layer ...")
    ui_claimants = "UI_Claimants_" + start_date + "_" + end_date
    sde_layers = ["USCB_Texas_Counties_Political", "USCB_Texas_Zip_Codes_2010", "TEA_Texas_School_Districts", "CoH_Council_Districts", "HGAC_Commissioner_Precincts", "TxDOT_Texas_State_House_Districts", "TxDOT_Texas_State_Senate_Districts", "TxDOT_Texas_US_House_Districts"]

    for sde_layer in sde_layers:
        print("        " + sde_layer)
        join_layer = r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN." + sde_layer
        claimants_joined = "Claimants_" + sde_layer

        arcpy.SpatialJoin_analysis(ui_claimants, join_layer, claimants_joined)

    print("        Abbreviating county names ...")
    arcpy.MakeFeatureLayer_management("Claimants_USCB_Texas_Counties_Political", 'claimants_counties_fl')
    arcpy.SelectLayerByAttribute_management('claimants_counties_fl', "NEW_SELECTION", '"NAME" IS NOT NULL')
    arcpy.CalculateField_management('claimants_counties_fl', "NAME", "Left([NAME], Len([NAME]) - 7)")

def finalize_claimants_layer():
    print("    Finalizing claimants layer ...")
    print("        Calculating attributes for " + "UI_Claimants_" + start_date + "_" + end_date + " ...")
    ui_claimants = "UI_Claimants_" + start_date + "_" + end_date
    fields = ["County", "ZIP", "SchoolDistNo", "SchoolDistName", "CoHCouncilNo", "CoHCouncilName", "CommNo", "CommName", "TXHouseNo", "TXHouseRep", "TXSenateNo", "TXSenateRep", "USHouseNo", "USHouseRep"]
    arcpy.DeleteField_management(ui_claimants, fields)

    print("            Adding field ...")
    for field in fields:
        print("                " + field)
        arcpy.AddField_management(ui_claimants, field, "TEXT")

    ui_claimants_fl = 'ui_claimants_fl'
    arcpy.MakeFeatureLayer_management(ui_claimants, ui_claimants_fl)

    print("            Copying attributes ...")

    # Copy attributes to Claimants_USCB_Texas_Counties_Political
    print("                Claimants_USCB_Texas_Counties_Political")
    arcpy.AddJoin_management(ui_claimants_fl, "ID", "Claimants_USCB_Texas_Counties_Political", "ID")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".CountyName", "[Claimants_USCB_Texas_Counties_Political.NAME]")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".County", "[Claimants_USCB_Texas_Counties_Political.NAME]")
    arcpy.RemoveJoin_management(ui_claimants_fl)

    # Copy attributes to Claimants_USCB_Texas_Zip_Codes_2010
    print("                Claimants_USCB_Texas_Zip_Codes_2010")
    arcpy.AddJoin_management(ui_claimants_fl, "ID", "Claimants_USCB_Texas_Zip_Codes_2010", "ID")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".Zip_Code", "[Claimants_USCB_Texas_Zip_Codes_2010.ZCTA5CE10]")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".ZIP", "[Claimants_USCB_Texas_Zip_Codes_2010.ZCTA5CE10]")
    arcpy.RemoveJoin_management(ui_claimants_fl)

    # Copy attributes to Claimants_TEA_Texas_School_Districts
    print("                Claimants_TEA_Texas_School_Districts")
    arcpy.AddJoin_management(ui_claimants_fl, "ID", "Claimants_TEA_Texas_School_Districts", "ID")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".SchoolDistNo", "[Claimants_TEA_Texas_School_Districts.SDLEA10]")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".SchoolDistName", "[Claimants_TEA_Texas_School_Districts.NAME]")
    arcpy.RemoveJoin_management(ui_claimants_fl)

    # Copy attributes to Claimants_CoH_Council_Districts
    print("                Claimants_CoH_Council_Districts")
    arcpy.AddJoin_management(ui_claimants_fl, "ID", "Claimants_CoH_Council_Districts", "ID")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".CoHCouncilNo", "[Claimants_CoH_Council_Districts.DISTRICT]")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".CoHCouncilName", "[Claimants_CoH_Council_Districts.MEMBER]")
    arcpy.RemoveJoin_management(ui_claimants_fl)

    # Copy attributes to Claimants_HGAC_Commissioner_Precincts
    print("                Claimants_HGAC_Commissioner_Precincts")
    arcpy.AddJoin_management(ui_claimants_fl, "ID", "Claimants_HGAC_Commissioner_Precincts", "ID")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".CommNo", '[Claimants_HGAC_Commissioner_Precincts.County] + " County Commissioner Precinct " + [Claimants_HGAC_Commissioner_Precincts.Precinct]')
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".CommName", "[Claimants_HGAC_Commissioner_Precincts.Commission]")
    arcpy.RemoveJoin_management(ui_claimants_fl)

    # Copy attributes to Claimants_TxDOT_Texas_State_House_Districts
    print("                Claimants_TxDOT_Texas_State_House_Districts")
    arcpy.AddJoin_management(ui_claimants_fl, "ID", "Claimants_TxDOT_Texas_State_House_Districts", "ID")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".TXHouseNo", "[Claimants_TxDOT_Texas_State_House_Districts.DIST_NBR]")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".TXHouseRep", "[Claimants_TxDOT_Texas_State_House_Districts.REP_NM]")
    arcpy.RemoveJoin_management(ui_claimants_fl)

    # Copy attributes to Claimants_TxDOT_Texas_State_Senate_Districts
    print("                Claimants_TxDOT_Texas_State_Senate_Districts")
    arcpy.AddJoin_management(ui_claimants_fl, "ID", "Claimants_TxDOT_Texas_State_Senate_Districts", "ID")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".TXSenateNo", "[Claimants_TxDOT_Texas_State_Senate_Districts.DIST_NBR]")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".TXSenateRep", "[Claimants_TxDOT_Texas_State_Senate_Districts.REP_NM]")
    arcpy.RemoveJoin_management(ui_claimants_fl)

    # Copy attributes to Claimants_TxDOT_Texas_US_House_Districts
    print("                Claimants_TxDOT_Texas_US_House_Districts")
    arcpy.AddJoin_management(ui_claimants_fl, "ID", "Claimants_TxDOT_Texas_US_House_Districts", "ID")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".USHouseNo", "[Claimants_TxDOT_Texas_US_House_Districts.DIST_NBR]")
    arcpy.CalculateField_management(ui_claimants_fl, ui_claimants + ".USHouseRep", "[Claimants_TxDOT_Texas_US_House_Districts.REP_NM]")
    arcpy.RemoveJoin_management(ui_claimants_fl)

    print("        Copying feature class to HGAC_UI_Claimants ...")
    hgac_ui_claimants = "HGAC_UI_Claimants"
    arcpy.FeatureClassToFeatureClass_conversion(ui_claimants, r"\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Requests\Workforce\UI_Claims\Default.gdb", hgac_ui_claimants)

def summarize_counts():
    print("    Summarizing claimant counts ...")

    # Summarize claimant counts for USCB_Texas_Counties_Political
    print("        USCB_Texas_Counties_Political")
    arcpy.Statistics_analysis('claimants_counties_fl', "Sum_USCB_Texas_Counties_Political", "ID COUNT", "NAME")

    # Summarize claimant counts for USCB_Texas_Zip_Codes_2010
    print("        USCB_Texas_Zip_Codes_2010")
    arcpy.Statistics_analysis("Claimants_USCB_Texas_Zip_Codes_2010", "Sum_USCB_Texas_Zip_Codes_2010", "ID COUNT", "ZCTA5CE10")

    # Summarize claimant counts for TEA_Texas_School_Districts
    print("        TEA_Texas_School_Districts")
    arcpy.Statistics_analysis("Claimants_TEA_Texas_School_Districts", "Sum_TEA_Texas_School_Districts", "ID COUNT", "SDLEA10")

    # Summarize claimant counts for CoH_Council_Districts
    print("        CoH_Council_Districts")
    arcpy.Statistics_analysis("Claimants_CoH_Council_Districts", "Sum_CoH_Council_Districts", "ID COUNT", "DISTRICT")

    # Summarize claimant counts for HGAC_Commissioner_Precincts
    print("        HGAC_Commissioner_Precincts")
    arcpy.Statistics_analysis("Claimants_HGAC_Commissioner_Precincts", "Sum_HGAC_Commissioner_Precincts", "ID COUNT", "Commission")

    # Summarize claimant counts for TxDOT_Texas_State_House_Districts
    print("        TxDOT_Texas_State_House_Districts")
    arcpy.Statistics_analysis("Claimants_TxDOT_Texas_State_House_Districts", "Sum_TxDOT_Texas_State_House_Districts", "ID COUNT", "DIST_NBR")
    arcpy.AddField_management("Sum_TxDOT_Texas_State_House_Districts", "DIST_NBR_STR", "TEXT")
    arcpy.CalculateField_management("Sum_TxDOT_Texas_State_House_Districts", "DIST_NBR_STR", "[DIST_NBR]")

    # Summarize claimant counts for TxDOT_Texas_State_Senate_Districts
    print("        TxDOT_Texas_State_Senate_Districts")
    arcpy.Statistics_analysis("Claimants_TxDOT_Texas_State_Senate_Districts", "Sum_TxDOT_Texas_State_Senate_Districts", "ID COUNT", "DIST_NBR")
    arcpy.AddField_management("Sum_TxDOT_Texas_State_Senate_Districts", "DIST_NBR_STR", "TEXT")
    arcpy.CalculateField_management("Sum_TxDOT_Texas_State_Senate_Districts", "DIST_NBR_STR", "[DIST_NBR]")

    # Summarize claimant counts for TxDOT_Texas_US_House_Districts
    print("        TxDOT_Texas_US_House_Districts")
    arcpy.Statistics_analysis("Claimants_TxDOT_Texas_US_House_Districts", "Sum_TxDOT_Texas_US_House_Districts", "ID COUNT", "DIST_NBR")


def copy_counts():
    print("    Copying claimant counts to administrative layers ...")

    # Copy claimant counts to HGAC_Counties_UI_Claims
    print("        HGAC_Counties_UI_Claims")
    arcpy.MakeFeatureLayer_management(r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN.HGAC_Counties_UI_Claims", 'counties_fl')

    print("            Joining ...")
    arcpy.AddJoin_management('counties_fl', "NAME", "Sum_USCB_Texas_Counties_Political", "NAME")

    print("            Copying counts ...")
    arcpy.CalculateField_management('counties_fl', "Global.GLOBAL_ADMIN.HGAC_Counties_UI_Claims.UICount", "[Sum_USCB_Texas_Counties_Political.COUNT_ID]")

    print("            Removing join ...")
    arcpy.RemoveJoin_management('counties_fl')

    # Copy claimant counts to HGAC_ZIP_Codes_UI_Claims
    print("        HGAC_ZIP_Codes_UI_Claims")
    arcpy.MakeFeatureLayer_management(r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN.HGAC_ZIP_Codes_UI_Claims", 'zip_fl')

    print("            Joining ...")
    arcpy.AddJoin_management('zip_fl', "Zip_Code", "Sum_USCB_Texas_Zip_Codes_2010", "ZCTA5CE10")

    print("            Copying counts ...")
    arcpy.CalculateField_management('zip_fl', "Global.GLOBAL_ADMIN.HGAC_ZIP_Codes_UI_Claims.UICount", "[Sum_USCB_Texas_Zip_Codes_2010.COUNT_ID]")

    print("            Filling null values ...")
    arcpy.SelectLayerByAttribute_management('zip_fl', "NEW_SELECTION", '"Sum_USCB_Texas_Zip_Codes_2010.OBJECTID" IS NULL')
    arcpy.RemoveJoin_management('zip_fl')
    arcpy.CalculateField_management('zip_fl', "UICount", "0")

    # Copy claimant counts to HGAC_School_Districts_UI_Claims
    print("        HGAC_School_Districts_UI_Claims")
    arcpy.MakeFeatureLayer_management(r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN.HGAC_School_Districts_UI_Claims", 'school_dist_fl')

    print("            Joining ...")
    arcpy.AddJoin_management('school_dist_fl', "ISD_ID", "Sum_TEA_Texas_School_Districts", "SDLEA10")

    print("            Copying counts ...")
    arcpy.CalculateField_management('school_dist_fl', "Global.GLOBAL_ADMIN.HGAC_School_Districts_UI_Claims.UICount", "[Sum_TEA_Texas_School_Districts.COUNT_ID]")

    print("            Filling null values ...")
    arcpy.SelectLayerByAttribute_management('school_dist_fl', "NEW_SELECTION", '"Sum_TEA_Texas_School_Districts.OBJECTID" IS NULL')
    arcpy.RemoveJoin_management('school_dist_fl')
    arcpy.CalculateField_management('school_dist_fl', "UICount", "0")

    # Copy claimant counts to HGAC_CoH_Council_Districts_UI_Claims
    print("        HGAC_CoH_Council_Districts_UI_Claims")
    arcpy.MakeFeatureLayer_management(r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN.HGAC_CoH_Council_Districts_UI_Claims", 'coh_council_fl')

    print("            Joining ...")
    arcpy.AddJoin_management('coh_council_fl', "DISTRICT", "Sum_CoH_Council_Districts", "DISTRICT")

    print("            Copying counts ...")
    arcpy.CalculateField_management('coh_council_fl', "Global.GLOBAL_ADMIN.HGAC_CoH_Council_Districts_UI_Claims.UICount", "[Sum_CoH_Council_Districts.COUNT_ID]")

    print("            Removing join ...")
    arcpy.RemoveJoin_management('coh_council_fl')

    # Copy claimant counts to HGAC_Commissioner_Precincts_UI_Claims
    print("        HGAC_Commissioner_Precincts_UI_Claims")
    arcpy.MakeFeatureLayer_management(r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN.HGAC_Commissioner_Precincts_UI_Claims", 'commissioner_fl')

    print("            Joining ...")
    arcpy.AddJoin_management('commissioner_fl', "Commission", "Sum_HGAC_Commissioner_Precincts", "Commission")

    print("            Copying counts ...")
    arcpy.CalculateField_management('commissioner_fl', "Global.GLOBAL_ADMIN.HGAC_Commissioner_Precincts_UI_Claims.UICount", "[Sum_HGAC_Commissioner_Precincts.COUNT_ID]")

    print("            Filling null values ...")
    arcpy.SelectLayerByAttribute_management('commissioner_fl', "NEW_SELECTION", '"Sum_HGAC_Commissioner_Precincts.OBJECTID" IS NULL')
    arcpy.RemoveJoin_management('commissioner_fl')
    arcpy.CalculateField_management('commissioner_fl', "UICount", "0")

    # Copy claimant counts to HGAC_State_House_Districts_UI_Claims
    print("        HGAC_State_House_Districts_UI_Claims")
    arcpy.MakeFeatureLayer_management(r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN.HGAC_State_House_Districts_UI_Claims", 'state_house_fl')

    print("            Joining ...")
    arcpy.AddJoin_management('state_house_fl', "DIST_NBR", "Sum_TxDOT_Texas_State_House_Districts", "DIST_NBR_STR")

    print("            Copying counts ...")
    arcpy.CalculateField_management('state_house_fl', "Global.GLOBAL_ADMIN.HGAC_State_House_Districts_UI_Claims.UICount", "[Sum_TxDOT_Texas_State_House_Districts.COUNT_ID]")

    print("            Filling null values ...")
    arcpy.SelectLayerByAttribute_management('state_house_fl', "NEW_SELECTION", '"Sum_TxDOT_Texas_State_House_Districts.OBJECTID" IS NULL')
    arcpy.RemoveJoin_management('state_house_fl')
    arcpy.CalculateField_management('state_house_fl', "UICount", "0")

    # Copy claimant counts to HGAC_State_Senate_Districts_UI_Claims
    print("        HGAC_State_Senate_Districts_UI_Claims")
    arcpy.MakeFeatureLayer_management(r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN.HGAC_State_Senate_Districts_UI_Claims", 'state_senate_fl')

    print("            Joining ...")
    arcpy.AddJoin_management('state_senate_fl', "DIST_NBR", "Sum_TxDOT_Texas_State_Senate_Districts", "DIST_NBR_STR")

    print("            Copying counts ...")
    arcpy.CalculateField_management('state_senate_fl', "Global.GLOBAL_ADMIN.HGAC_State_Senate_Districts_UI_Claims.UICount", "[Sum_TxDOT_Texas_State_Senate_Districts.COUNT_ID]")

    print("            Removing join ...")
    arcpy.RemoveJoin_management('state_senate_fl')

    # Copy claimant counts to HGAC_US_House_Districts_UI_Claims
    print("        HGAC_US_House_Districts_UI_Claims")
    arcpy.MakeFeatureLayer_management(r"Database Connections\Global_SDE_(Global_Admin).sde\Global.GLOBAL_ADMIN.HGAC_US_House_Districts_UI_Claims", 'us_house_fl')

    print("            Joining ...")
    arcpy.AddJoin_management('us_house_fl', "CD116FP", "Sum_TxDOT_Texas_US_House_Districts", "DIST_NBR")

    print("            Copying counts ...")
    arcpy.CalculateField_management('us_house_fl', "Global.GLOBAL_ADMIN.HGAC_US_House_Districts_UI_Claims.UICount", "[Sum_TxDOT_Texas_US_House_Districts.COUNT_ID]")

    print("            Removing join ...")
    arcpy.RemoveJoin_management('us_house_fl')

def main():
    arcpy.env.workspace = r"\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Requests\Workforce\UI_Claims\Default.gdb"
    arcpy.env.overwriteOutput = True

    prepare_claimants_layer()
    spatially_join()
    finalize_claimants_layer()
    summarize_counts()
    copy_counts()

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting HGAC Workforce Solutions UI Claims Data Calculator (Workforce Solutions Version)")
    print("Version 1.0")
    print("Last update: 7/28/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    start_date = raw_input("Please enter start date (yyyymmdd): ")
    end_date = raw_input("Please enter end date (yyyymmdd): ")
    main() # Run main function

    end_time = datetime.datetime.now()
    print("\n")
    print("End time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

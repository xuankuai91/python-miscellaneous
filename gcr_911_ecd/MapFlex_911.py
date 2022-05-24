import arcpy, datetime, os, sys
sys.path.append(r'\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Process Automation\Modules\Bin')
import earcpy

def extract_layer(src_layer, dst, dst_layer):
    if src_layer[-15:] == "Model_Buildings":
        # Extract selected school data from the Model_Buildings layer
        print("                Schools")
        school_query = "{} IN ('EDU_SCHOOL','EDU_SCHOOL_PRIV','EDU_SCHOOL_PUB','EDU_SCHOOL_REL')".format(arcpy.AddFieldDelimiters(src_layer, "O_BldgType"))
        arcpy.FeatureClassToFeatureClass_conversion(src_layer, dst, "Schools", school_query)

        # Extract selected hospital data from the Model_Buildings layer
        print("                Hospitals")
        hospital_query = "{} IN ('HSP','HSP_VET')".format(arcpy.AddFieldDelimiters(src_layer, "O_BldgType"))
        arcpy.FeatureClassToFeatureClass_conversion(src_layer, dst, "Hospitals", hospital_query)

    elif src_layer[-20:] == "HGAC_13_County_Parks":
        # Extract the HGAC_13_County_Parks layer without the related tables and relationship classes
        arcpy.FeatureClassToFeatureClass_conversion(src_layer, dst, dst_layer)

        print("            Cleaning up ...")
        tables = ["HGAC_13_County_Parks_Awards", "HGAC_13_County_Parks_Features", "HGAC_13_County_Parks_Parcels"]
        for table in tables:
            arcpy.Delete_management(table)

    else:
        # Extract other normal layers
        arcpy.Copy_management(src_layer, dst_layer)

def main():
    workspace = r"\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Process Automation\Project Folder\Monthly Runs\MapFlex"

    base_gdb = os.path.join(workspace, "MapFlexBackup.gdb")

    extract_gdb = os.path.join(workspace, r"Extracts\MapFlexUpdates.gdb")
    arcpy.env.workspace = extract_gdb
    arcpy.env.overwriteOutput = True

    username = raw_input("    Please enter your username (e.g., CBERRY for Chuck Berry): ")

    # Extract CE and Global SDE layers
    print("    Extracting CE and Global SDE layers ...")
    ce_sde = r"Database Connections\CE_SDE.sde"
    global_sde = r"Database Connections\Global_SDE.sde"
    hgac_911_sde = r"Database Connections\HGAC_911_SDE.sde"

    ce_layers = ["HGAC_13_County_Parks", "HGAC_15_County_CRP_Streams", "Model_Buildings"]
    global_layers = ["HGAC_Water_Detailed", "NTAD_Raillines", "TxDOT_Highway_Milemarkers"]
    layers = ce_layers + global_layers

    # Compose layer's full path
    for layer in layers:
        print("        " + layer)
        if layer in ce_layers:
            sde = ce_sde
            prefix = "CE.CE_ADMIN."

        else:
            sde = global_sde
            prefix = "Global.Global_Admin."

        base_layer = os.path.join(base_gdb, layer) # Set the full path to the G drive backup which the schema comparison is based on
        test_layer = os.path.join(sde, prefix + layer) # Set the full path to the SDE layer whose schema will be compared

        if arcpy.Exists(test_layer):
            # Compare schemas and extract data if the SDE layer exists
            try:
                # Set the geometry fields to be omitted based on layer's geometry type
                if arcpy.Describe(test_layer).shapeType == 'Point':
                    omit_fields = ["Shape"]

                elif arcpy.Describe(test_layer).shapeType == 'Polyline':
                    omit_fields = ["Shape", "Shape_Length", "Shape.len"]

                elif arcpy.Describe(test_layer).shapeType == 'Polygon':
                    omit_fields = ["Shape", "Shape_Length", "Shape.len", "Shape_Area", "Shape.area"]

                else:
                    print("{} is not a point, polyline, or polygon layer.".format(layer))

            except:
                print("{} is not a feature class.".format(layer))

            # Compare schema between the SDE layer and the G drive backup
            print("            Comparing schemas ...")
            compare_result = arcpy.FeatureCompare_management(base_layer, test_layer, "OBJECTID", "SCHEMA_ONLY", omit_field=omit_fields, continue_compare="CONTINUE_COMPARE")
            
            if compare_result.getOutput(1) == "true":
                print("                Did not change")

                print("            Backing up ...")
                arcpy.Copy_management(test_layer, base_layer) # Back up the current SDE layer to G drive if the schema is the same

                print("            Extracting from the SDE layer ...")
                src_layer = test_layer # Set the extraction source to the SDE layer if the schema is the same

            else:
                print("                Changed")
                print("            Extracting from the backup layer ...")
                src_layer = base_layer # Set the extraction source to the G drive backup if the schema is changed
            
            extract_layer(src_layer, extract_gdb, layer)

        else:
            # Print message is the SDE layer does not exist
            print("            Layer does not exist")

    # Extract H-GAC 911 SDE layers
    print("    Extracting H-GAC 911 SDE layers ...")
    hgac_911_layers = ["Brazoria_KeyMap_Ltr", "Brazoria_KeyMap_Page", "Brazoria_Utility", "cell_towers_911", "cell_sectors_911", "Rural911", "STARMap"]

    for layer in hgac_911_layers:
        print("        " + layer)
        src_data = os.path.join(hgac_911_sde, "HGAC_911.HGAC911_ADMIN." + layer)

        print("            Extracting ...")
        arcpy.Copy_management(src_data, layer)

    # Select test points in HGAC_911.HGAC911_ADMIN.hgac911_address layer
    address_layer = os.path.join(extract_gdb, "Rural911\hgac911_address")
    query = "{} = 'TESTPOINT'".format(arcpy.AddFieldDelimiters(address_layer, "StreetName"))
    arcpy.MakeTableView_management(address_layer, 'address_layer_tv')
    arcpy.SelectLayerByAttribute_management('address_layer_tv', "NEW_SELECTION", query)

    # Populate date fields in HGAC_911.HGAC911_ADMIN.hgac911_address table
    print("            Populating date fields ...")
    now = datetime.datetime.now()
    now_date = "{}/{}/{}".format(now.year, now.month, now.day)
    now_time = datetime.datetime.strftime(now, "%#I:%#M:%#S %p")

    date_fields = ["Notes1", "AT_DATETIME", "SP_DATETIME"]
    for date_field in date_fields:
        print("                " + date_field)
        arcpy.CalculateField_management('address_layer_tv', date_field, "CDate(#{}#)".format(now_date))

    print("                CR_DATETIME")
    arcpy.CalculateField_management('address_layer_tv', "CR_DATETIME", "CDate(#{}#)".format(now_date + " " + now_time))

    # Populate name fields in HGAC_911.HGAC911_ADMIN.hgac911_address table using user input
    print("            Populating username fields ...")
    username_fields = ["USERNAME", "CR_USERNAME", "AT_USERNAME", "SP_USERNAME"]
    for username_field in username_fields:
        print("                " + username_field)
        arcpy.CalculateField_management('address_layer_tv', username_field, '\"' + username + '\"')

    # Clean up the geodatabase
    print("    Cleaning up MapFlexUpdates.gdb ...")
    arcpy.Delete_management(os.path.join(extract_gdb, r"STARMap\hgac_zipcodes"))
    arcpy.Compact_management(extract_gdb)

    # Zip the geodatabase
    print("    Zipping geodatabase ...")
    earcpy.zip_folder(extract_gdb)

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting MapFlex 911 Extract tool")
    print("Version 1.0")
    print("Last update: 10/30/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

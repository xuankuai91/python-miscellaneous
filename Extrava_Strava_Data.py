import arcpy, datetime, os, csv

def main():
    root = r"\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Data_Development\To_Evaluate\Strava"

    years = ["2018", "2019", "2020"]
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

    for year in years:
        print("    " + year)

        for month in months:
            print("        " + month)
            folder = os.path.join(root, "{}_Data".format(year), "all_edges_{}_{}_ride".format(month, year))
            files = os.listdir(folder)
            table = os.path.join(folder, files[0])
            shape = os.path.join(folder, files[3])

            print("            Creating geodatabase ...")
            arcpy.Delete_management(os.path.join(folder, "Default.gdb"))
            arcpy.CreateFileGDB_management(folder, "Default.gdb")

            workspace = os.path.join(folder, "Default.gdb")
            arcpy.env.workspace = workspace
            arcpy.env.overwriteOutput = True

            print("            Creating feature class ...")
            arcpy.CopyFeatures_management(shape, "out_shape")
            arcpy.TableToTable_conversion(table, workspace, "out_table") # Use "out_table" as output table name because "table" is a reserved name

            with open(table, 'rb') as f:
                reader = csv.reader(f)
                field_names = reader.next()[3:]

            for field_name in field_names:
                arcpy.AddField_management("out_shape", field_name, "LONG")

            print("            Summarizing data ...")
            stats_fields = []
            out_fields = arcpy.ListFields("out_table", "*_count")

            for out_field in out_fields:
                stats_fields.append([out_field.name, "SUM"])

            arcpy.Statistics_analysis("out_table", "sum_counts", stats_fields, "edge_uid")

            annual_gdb = os.path.join(root, "{}_Data".format(year), "Default.gdb")

            if month == "jan":
                print("            Copying January table as master ...")
                annual_table = "Strava_Bike_Usage_{}".format(year)
                arcpy.TableToTable_conversion("sum_counts", annual_gdb, annual_table)

            else:
                print("            Adding data ...")
                annual_table = os.path.join(annual_gdb, "Strava_Bike_Usage_{}".format(year))

                stats_fields = []
                out_fields = arcpy.ListFields(annual_table, "*_count")

                for out_field in out_fields:
                    stats_fields.append([out_field.name, "SUM"])

                arcpy.Append_management("sum_counts", annual_table)

        arcpy.Statistics_analysis(annual_table, os.path.join(annual_gdb, "Strava_Bike_Usage"), stats_fields, "edge_uid")

        annual_gdb = os.path.join(root, "{}_Data".format(year), "Default.gdb")
        arcpy.env.workspace = annual_gdb
        arcpy.env.overwriteOutput = True
        annual_shape = "Strava_Bike_Usage_{}1".format(year)

        stats_fields = []
        out_fields = arcpy.ListFields(annual_shape, "*_count")

        for out_field in out_fields:
            stats_fields.append([out_field.name, "SUM"])

        arcpy.MakeFeatureLayer_management(annual_shape, 'fl')
        arcpy.AddJoin_management('fl', "edgeUID", "Strava_Bike_Usage", "edge_uid")

        for stats_field in stats_fields:
            print("                    " + stats_field[0])
            arcpy.CalculateField_management('fl', "Strava_Bike_Usage_{}1.{}".format(year, stats_field[0]), "[Strava_Bike_Usage_{}1.{}] + [Strava_Bike_Usage.SUM_SUM_{}]".format(year, stats_field[0], stats_field[0]))

        arcpy.RemoveJoin_management('fl')

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

import arcpy, datetime, os, json, math
import pandas as pd

def write_attributes(schema_df, cell_towers_df, cell_tower_index, row):
    for schema_index in schema_df.index:
        old_field = schema_df['Current'][schema_index]
        new_field = schema_df['FieldName'][schema_index]
        field_type = schema_df['Type'][schema_index]

        if not pd.isnull(old_field):
            field_value = cell_towers_df[old_field][cell_tower_index]

            if not pd.isnull(field_value):
                print("                    " + old_field + " -> " + new_field + ": " + field_type + ", " + str(field_value))
                if field_type == 'DOUBLE':
                    row.setValue(new_field, field_value)
                elif field_type == 'DATE':
                    row.setValue(new_field, datetime.datetime.strptime(field_value, '%m/%d/%Y'))
                else:
                    if str(field_value).isdigit():
                        row.setValue(new_field, str(field_value))
                    else:
                        row.setValue(new_field, field_value)
            else:
                print("                    " + old_field + " -> " + new_field + ": " + field_type + ", NULL")
                continue
        else:
            print("                    ----NEW ATTRIBUTE: " + new_field + "----")
            continue

def finalize_towers():
    print("        Writing MAX_NumberofSectors field ...")
    arcpy.AddField_management("cell_towers_911_temp", "MAX_NumberofSectors", "TEXT")

    stats_fields = [["TowerID", "COUNT"], ["NumberofSectors", "MAX"]]
    arcpy.Statistics_analysis("cell_towers_911_temp", "Summary_Stats", stats_fields, "TowerID")
    arcpy.MakeFeatureLayer_management("cell_towers_911_temp", 'fl')
    arcpy.AddJoin_management('fl', "TowerID", "Summary_Stats", "TowerID")
    arcpy.CalculateField_management('fl', "cell_towers_911_temp.MAX_NumberofSectors", "[Summary_Stats.MAX_NumberofSectors]")

    print("        Compiling Comment field ...")
    tower_dict = {}
    cursor = arcpy.da.SearchCursor("cell_towers_911_temp", ["TowerID", "Comment"])
    
    for row in cursor:
        if not row[0] in tower_dict:
            tower_dict[row[0]] = [row[1]]
        else:
            tower_dict[row[0]].append(row[1])

    del cursor
    
    cursor = arcpy.da.UpdateCursor("cell_towers_911_temp", ["TowerID", "Comment"])
    
    for row in cursor:
        if row[0] in tower_dict:
            row[1] = ",".join(map(str, tower_dict[row[0]]))
            cursor.updateRow(row)

    del cursor

    arcpy.Delete_management("Summary_Stats")

def finalize_sectors():
    arcpy.CalculateField_management("cell_sectors_911", "SectorID", "[Cell_Site_ID] + \"_\" + [Sector_Number]")
    arcpy.CalculateField_management("cell_sectors_911", "UID", "[UID] + \"-\" + [Comment]")


def main():
    print("    Creating geodatabase ...")
    work_directory = r"\\Hgac.net\FileShare\ArcGIS\DataSvcs\GIS\Process Automation\Project Folder\Tools and Applications\Cell Sector Check"
    now = datetime.datetime.now()
    date = '{:02d}'.format(now.year) + '{:02d}'.format(now.month) + '{:02d}'.format(now.day)
    time = '{:02d}'.format(now.hour) + '{:02d}'.format(now.minute)
    gdb = "CellSectors911_" + date + "_" + time + ".gdb"

    arcpy.CreateFileGDB_management(os.path.join(work_directory, "GDBs"), gdb)

    arcpy.env.workspace = os.path.join(work_directory, "GDBs", gdb)
    arcpy.env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(2278)

    wgs_1984 = arcpy.SpatialReference(4326)
    nad_1983 = arcpy.SpatialReference(2278)

    # Create empity feature classes
    print("    Creating empity feature classes ...")
    print("        cell_towers_911")
    print("            Reading schema ...")
    cell_tower_schema_csv = os.path.join(work_directory, "Supporting_Docs\CellTower_SchemaOutput.csv")
    cell_tower_schema_df = pd.read_csv(cell_tower_schema_csv)

    print("            Creating feature class ...")
    arcpy.CreateFeatureclass_management(os.path.join(work_directory, "GDBs", gdb), "cell_towers_911_temp", "POINT", spatial_reference=nad_1983)

    print("            Adding fields ...")
    for schema_index in cell_tower_schema_df.index:
        print("                " + cell_tower_schema_df['FieldName'][schema_index])
        arcpy.AddField_management("cell_towers_911_temp", cell_tower_schema_df['FieldName'][schema_index], cell_tower_schema_df['Type'][schema_index])

    cell_towers_cursor = arcpy.InsertCursor("cell_towers_911_temp")

    print("        cell_sectors_911")
    print("            Reading schema ...")
    cell_sector_schema_csv = os.path.join(work_directory, "Supporting_Docs\CellSector_SchemaOutput.csv")
    cell_sector_schema_df = pd.read_csv(cell_sector_schema_csv)

    print("            Creating feature class ...")
    arcpy.CreateFeatureclass_management(os.path.join(work_directory, "GDBs", gdb), "cell_sectors_911", "POLYGON", spatial_reference=nad_1983)

    print("            Adding fields ...")
    for schema_index in cell_sector_schema_df.index:
        print("                " + cell_sector_schema_df['FieldName'][schema_index])
        arcpy.AddField_management("cell_sectors_911", cell_sector_schema_df['FieldName'][schema_index], cell_sector_schema_df['Type'][schema_index])

    cell_sectors_cursor = arcpy.InsertCursor("cell_sectors_911")

    # Read cell towers data
    print("    Reading cell towers data ...")
    cell_towers_csv = os.path.join(work_directory, "MapFlexDataFormat_Check.csv")
    cell_towers_df = pd.read_csv(cell_towers_csv)

    for index in cell_towers_df.index:
        print("    Creating cell towers and cell sectors ...")
        print("        " + str(cell_towers_df['SiteID'][index]))

        # Load fields
        latitude = cell_towers_df['Latitude'][index]
        longitude = cell_towers_df['Longitude'][index]
        radius = cell_towers_df['Radius'][index]
        bearing = math.radians(cell_towers_df['Bearing'][index])
        angle = math.radians(cell_towers_df['Angle'][index])

        # Create cell tower geometry
        print("            Creating cell tower ...")
        print("                Writing geometry ...")
        cell_tower = arcpy.PointGeometry(arcpy.Point(longitude, latitude), wgs_1984).projectAs(nad_1983)

        # Insert tower geometry to cell_towers_911 with attributes
        cell_tower_row = cell_towers_cursor.newRow()
        cell_tower_row.shape = cell_tower

        print("                Writing attributes ...")
        write_attributes(cell_tower_schema_df, cell_towers_df, index, cell_tower_row)

        print("                Inserting geometry to cell_towers_911 ...")
        cell_towers_cursor.insertRow(cell_tower_row)

        print("            Creating cell sector ...")
        # Create split line
        print("                Creating split line ...")
        x = json.loads(cell_tower.JSON)['x']
        y = json.loads(cell_tower.JSON)['y']
        x_1 = x + radius * 5280 * math.sin(bearing + (angle / 2))
        y_1 = y + radius * 5280 * math.cos(bearing + (angle / 2))
        x_2 = x + radius * 5280 * math.sin(bearing - (angle / 2))
        y_2 = y + radius * 5280 * math.cos(bearing - (angle / 2))

        vertices = [[x_1, y_1], [x, y], [x_2, y_2]]
        split_line = arcpy.Polyline(arcpy.Array([arcpy.Point(*coordinates) for coordinates in vertices]), nad_1983)

        # Create buffer
        print("                Creating buffer ...")
        cell_tower_buffer = cell_tower.buffer(radius * 5280)

        # Split buffer geometry
        print("                Spliting buffer ...")
        cell_sectors = cell_tower_buffer.cut(split_line)

        for sector in cell_sectors: # Determine smaller and larger sectors
            if sector.area == min(cell_sectors[0].area, cell_sectors[1].area):
                smaller_sector = sector
            else:
                larger_sector = sector

        if angle <= 180: # Determine which sector to use, smaller or larger, based on spread angle
            cell_sector = smaller_sector
        else:
            cell_sector = larger_sector

        # Insert sector geometry to cell_sectors_911 with attributes
        cell_sector_row = cell_sectors_cursor.newRow()
        cell_sector_row.shape = cell_sector

        print("                Writing attributes ...")
        write_attributes(cell_sector_schema_df, cell_towers_df, index, cell_sector_row)

        print("                Inserting geometry to cell_towers_911 ...")
        cell_sectors_cursor.insertRow(cell_sector_row)

    print("    Finalizing cell_towers_911 ...")
    finalize_towers()

    print("        Consolidating layer ...")
    arcpy.FeatureClassToFeatureClass_conversion("cell_towers_911_temp", os.path.join(work_directory, "GDBs", gdb), "cell_towers_911", "NumberOfSectors = MAX_NumberofSectors")
    arcpy.Delete_management("cell_towers_911_temp")

    print("    Finalizing cell_sectors_911 ...")
    finalize_sectors()

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print("Starting Cell Sector Check tool")
    print("Version 1.0")
    print("Last update: 7/31/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("End time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

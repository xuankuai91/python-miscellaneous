import arcpy, datetime

def main():
    workspace = r"Database Connections\Global_SDE_(Global_Admin).sde"
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    print("    HGAC_COVID_19_TSA_Q_Info")
    tsa_q = r"Global.GLOBAL_ADMIN.HGAC_COVID_19_TSA_Q_Info"

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

    print("Starting Calculate TSA Q Daily COVID-19 Numbers tool")
    print("Version 1.2")
    print("Last update: 9/18/2020")
    print("Support: Xuan.Kuai@h-gac.com" + "\n")
    print("Start time: " + str(start_time) + "\n")

    main() # Run main function

    end_time = datetime.datetime.now()
    print("\nEnd time: " + str(end_time) + "\n")
    print("Time elapsed: " + str(end_time - start_time) + "\n")

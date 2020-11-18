import arcpy, datetime, os

def compose_single_date_query(table, date_field, day, operator):
    date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(day.year, day.month, day.day)
    query = "{} {} {}".format(arcpy.AddFieldDelimiters(table, date_field), operator, date)

    return query

def compose_double_date_query(table, date_field, start_day=None, end_day=None, period=None):
    if start_day is None:
        start_day = end_day - datetime.timedelta(period - 1)

    elif end_day is None:
        end_day = start_day + datetime.timedelta(period - 1)

    start_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(start_day.year, start_day.month, start_day.day)
    end_day_date = "'{:02d}-{:02d}-{:02d} 00:00:00'".format(end_day.year, end_day.month, end_day.day)
    query = "{} BETWEEN {} AND {}".format(arcpy.AddFieldDelimiters(table, date_field), start_day_date, end_day_date)

    return query

def calculate_difference(table, field, query_1, query_2):
    cursor_1 = arcpy.da.SearchCursor(table, [field], query_1)
    for row_1 in cursor_1:
        value_1 = row_1[0]

    cursor_2 = arcpy.da.SearchCursor(table, [field], query_2)
    for row_2 in cursor_2:
        value_2 = row_2[0]

    difference = value_1 - value_2

    return difference

def list_values(table, field, query):
    cursor = arcpy.da.SearchCursor(table, [field], query)
    values = [row[0] for row in cursor if row[0] is not None]

    return values

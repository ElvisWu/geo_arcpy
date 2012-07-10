import arcpy, os

infile = 'C:\\Users\\Aaron\\Downloads\\Places\\Places\\Places.shp'
path, feature = os.path.split(infile)

arcpy.env.workspace = "CURRENT"

srows = arcpy.SearchCursor(infile)
row = srows.next()
while row:
    exp = "DATA" + "='" + str(row.getValue("DATA")) + "'"
    arcpy.Select_analysis(infile, path + "\\" + str(row.getValue("DATA")) + ".shp", exp)
    row = srows.next()
    
del row
del srows
    
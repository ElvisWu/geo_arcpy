# Select by bearing
#
# Assigns direction bearing to line feature classes based on start and end vertices
#
# Arguments
#
# Infile (0) - input line file
#
# Created by: Aaron Burgess
# Date: 05/08/2012
# Python 2.6.8
#####################################################################################
# import modules
import arcpy, traceback, sys, os, tempfile

# argument(s)
infile = arcpy.GetParameterAsText(0)

# set workspace
arcpy.env.workspace = "CURRENT"
temp_dir = tempfile.mkdtemp()
temp = os.path.split(temp_dir)
temp2 = r'C:\Temp\temp2.shp'
tbl1 = "tbl1"
tbl2 = "tbl2"
id_field = "NID"

# main
def adder(infiles):
    arcpy.AddField_management(temp2, "X", "DOUBLE")
    arcpy.AddField_management(temp2, "Y", "DOUBLE")
    desc = arcpy.Describe(temp2)
    shapefieldname = desc.ShapeFieldName
    srows = arcpy.UpdateCursor(temp2)
    for srow in srows:
        feat = srow.getValue(shapefieldname)
        pnt = feat.getPart()
        srow.X = pnt.X
        srow.Y = pnt.Y
        srows.updateRow(srow)
    del srow
    del srows

def direction(infiles):
    arcpy.AddField_management(infiles, "BEARING", "TEXT")
    srows = arcpy.UpdateCursor(infiles)
    count = 0
    past_x = None
    past_y = None
    past_id = None
    for row in srows:
        if count != 0:
            if (row.X > past_x and row.Y < past_y and row.NID == past_id):
                row.BEARING = "NE"
            elif (row.X > past_x and row.Y > past_y and row.NID == past_id):
                row.Bearing = "SE"
            elif (row.X < past_x and row.Y > past_y and row.NID == past_id):
                row.Bearing = "SW"
            elif (row.X < past_x and row.Y < past_y and row.NID == past_id):
                row.Bearing = "NW"
            elif (row.X == past_x and row.Y < past_y and row.NID == past_id):
                row.Bearing = "N"
            elif (row.X > past_x and row.Y == past_y and row.NID == past_id):
                row.Bearing = "E"
            elif (row.X == past_x and row.Y > past_y and row.NID == past_id):
                row.Bearing = "S"
            elif (row.X < past_x and row.Y == past_y and row.NID == past_id):
                row.Bearing = "W"
            else:
                row.Bearing = ""
            srows.updateRow(row)
            count += 1
            past_x = row.getValue("X")
            past_y = row.getValue("Y")
            past_id = row.getValue("NID")
    del row
    del srows
        
def update(infiles, temp_file):
    arcpy.AddField_management(infiles, "BEARING", "TEXT")
    arcpy.MakeFeatureLayer_management(infiles, tbl1)
    arcpy.MakeTableView_management(temp_file, tbl2, "\"BEARING\" <> ''")
    arcpy.JoinField_management(tbl1, id_field, tbl2, id_field)
    jrows = arcpy.UpdateCursor(tbl1)
    for jrow in jrows:
        bear = jrow.getValue("tbl2.BEARING")
        jrow.BEARING = bear
        jrows.updateRow(jrow)
    arcpy.RemoveJoin_management(tbl1, tbl2)
    del jrow
    del jrows
            
try:
    if arcpy.Exists(temp2):
        arcpy.Delete_management(temp2)
    arcpy.AddField_management(infile, "NID", "LONG")
    nrows = arcpy.UpdateCursor(infile)
    ncount = 0
    for nrow in nrows:
        nrow.NID = ncount
        nrows.updateRow(nrow)
        ncount = ncount + 1
    del nrow
    del nrows
    arcpy.FeatureVerticesToPoints_management(infile, temp2, "BOTH_ENDS")
    adder(temp2)
    direction(temp2)
    update(infile, temp2)
    arcpy.DeleteField_management(infile, "NID")
    
except:
    # begin error handling
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = 'PYTHON ERRORS:\nTraceback Info:\n' + tbinfo + 'n\Error Info:\n'
    msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + '\n'
    
    # prints error messages in the Progress dialog box
    arcpy.AddError(msgs)
    arcpy.AddError(pymsg)
    
    # prints messages in the Progress dialog box
    print msgs
    print pymsg
    
    arcpy.AddMessage(arcpy.GetMessages(1))
    
    print arcpy.GetMessage(1) 
# Street Intersection Creator
#
# Creates point for each street intersection and field listing the intersection name
#
# Arguments
#
# infile(0) - the input street centerline file
# names(1) - the field containing the street names
# outfile(2) - the desired output file
#
# Created by: Aaron Burgess
# Date: 5/8/2012
# Python 2.6.2
######################################################################################
# import modules
import arcpy, traceback, sys, shutil, tempfile

# arguments
infile = arcpy.GetParameterAsText(0)
name = arcpy.GetParameterAsText(1)
outfile = arcpy.GetParameterAsText(2)

arcpy.env.workspace = "CURRENT"

# global variables
tmp_dir = tempfile.mkdtemp()
temp = tmp_dir+"temp.shp"
temp2 = "temp.shp"
      
def nodes(infiles, names, outfiles):
    arcpy.AddField_management(infiles, "INTERSECT", "TEXT", "", "", 150)
    arcpy.Intersect_analysis(infiles, temp2, "ALL", "", "POINT")
    arcpy.MakeFeatureLayer_management(temp2, "temp2")
    srows = arcpy.UpdateCursor("temp2")
    for srow in srows:
        fid = srow.getValue("FID")
        arcpy.SelectLayerByAttribute_management("temp2", "NEW_SELECTION", "\"FID\" = " + fid)
        new_streets = []
        srows2 = arcpy.SearchCursor("temp2")
        for row in srows2:
            streets = row.getValue(names)
            new_streets.append(streets)
        final_streets = []
        for streeter in new_streets:
            if streeter not in final_streets:
                final_streets.append(streeter)
        fin_intersect = " & ".join(final_streets)
        srow.INTERSECT = fin_intersect
        srows.updateRow(srow)
    arcpy.SelectLayerByAttribute_management("temp2", "CLEAR_SELECTION")
    arcpy.CopyFeatures_management("temp2", outfiles)
    del row
    del srows2
    del srow
    del srows

# main
try:
    nodes(infile, name, outfile)
    
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

finally:
    shutil.rmtree(tmp_dir)
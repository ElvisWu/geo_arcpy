# Adjacency Matrix for ArcGIS
#
# Takes a given feature class(es) and creates
# an adjacency table showing nearest neighbors
# of each row or observation
#
# Aaron Burgess
# Created: Jan 2012
# Python 2.6
# ArcGIS 10 (arcpy module)
#########################################################
# import module
import arcpy, sys, traceback

arcpy.env.workspace = "CURRENT"

# arguments
infile = arcpy.GetParameterAsText(0)
field = arcpy.GetParameterAsText(1)
outfile = arcpy.GetParameterAsText(2)

# variables
layer = "temp"
count = 0

try:
    arcpy.SetProgressor("step", "Gettin' Loaded......", 0, 5, 1)
    if arcpy.Exists(layer):
        arcpy.Delete_management(layer)
        
    f = open(outfile +".csv","a")
    f.write(",Origin,\n")
    
    arcpy.MakeFeatureLayer_management(infile, layer)
    srows = arcpy.SearchCursor(layer)
    
    arcpy.SetProgressorPosition()
    arcpy.SetProgressorLabel("Entering the Matrix......")
    arcpy.AddMessage("\nBe patient.")
    arcpy.AddMessage("How's your day so far?")
    for srow in srows:
        count += 1
        end = layer + str(count)
        name = srow.getValue(field)
        query = '"' + str(field) + '" =' + "'" + str(name) + "'"
        temp_feat = "temp"
        new_lyr = end + "_lyr"
        sel_lyr = end + "_lyr2"
        o_point = "point" + str(count)
        d_point = "d_point" + str(count)
        distance = "NEAR_DIST"
        desc = arcpy.Describe(layer)
        arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", query )
        arcpy.CopyFeatures_management(layer,temp_feat)
        arcpy.MakeFeatureLayer_management(temp_feat, new_lyr)
        arcpy.FeatureToPoint_management(new_lyr, o_point)
        arcpy.SelectLayerByLocation_management(layer, "SHARE_A_LINE_SEGMENT_WITH", new_lyr)
        arcpy.CopyFeatures_management(layer, sel_lyr)
        arcpy.FeatureToPoint_management(sel_lyr, d_point)
        arcpy.Near_analysis(d_point, o_point)
        f.write("," + name + "," + "\n")
        f.write("Neighbors,")
        arcpy.SetProgressorPosition()
        arcpy.SetProgressorLabel("Calculating Neighbors...")
        lrows = arcpy.SearchCursor(sel_lyr)
        for lrow in lrows:
            name2 = lrow.getValue(field)
            f.write(name2 + ",")
        f.write("\n")
        f.write("Distance,")
        arcpy.SetProgressorPosition()
        arcpy.SetProgressorLabel("Calculating Distance....")
        prows = arcpy.SearchCursor(d_point, "", desc.spatialReference)
        for prow in prows:
            dist = prow.getValue(distance)
            f.write(str(dist) + ",")
        f.write("\n")
        arcpy.ResetProgressor()
    
    arcpy.SetProgressorPosition()
    arcpy.SetProgressorLabel("Cleaning up.....")
    arcpy.AddMessage("I'm deleting files created for the purpose of calculation.")
    arcpy.Delete_management(temp_feat)
    arcpy.Delete_management(layer)
    arcpy.Delete_management(new_lyr)
    arcpy.Delete_management(sel_lyr)
    arcpy.Delete_management(o_point)
    arcpy.Delete_management(d_point)
    
    f.write("\n")    
    f.close
    
    arcpy.AddMessage("Thanks for hanging in there!")
    arcpy.SetProgressorPosition()
    arcpy.SetProgressorLabel("Almost there!")

except:
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
    if srow:
        del srow
    if srows:
        del srows
    if lrow:
        del lrow
    if lrows:
        del lrows
    if prow:
        del prow
    if prows:
        del prows
    arcpy.ResetProgressor()
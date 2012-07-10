# Featurator Program
#
# Creates a select by attribute and immediately
# turns the selection into a feature class for speed
#
# Arguments
#
# 0 - Feature Class
# 1 - Selection Query
# 2 - Output Feature
# 3 - Output Table
#
# Aaron Burgess
# Jan 2012
# Python 2.6
# ArcGIS 10.1
#########################################################
# import module
import arcpy, sys, os, traceback

arcpy.env.workspace = ("CURRENT")

try:
    def layer_create(infile, layer, query):
        """ Creates the feature from selection. """
        if arcpy.Exists(layer):
            arcpy.Delete_management(layer)
        arcpy.MakeFeatureLayer_management(infile, layer, query)
    
    def make_feature(layer, outfile):
        """ Turns layer into feature class. """
        if arcpy.Exists(outfile):
            arcpy.Delete_management(outfile)
        arcpy.CopyFeatures_management(layer, outfile)
        
    def make_table(layer, outtable):
        """ Creates table of queried layer. """
        if arcpy.Exists(outtable):
            arcpy.Delete_management(outtable)
        arcpy.CopyRows_management(layer, outtable)
    
    def select_features(inlayer, select_type, compare_layer):
        """ Creates select by location """
        arcpy.SelectLayerByLocation_management(inlayer, select_type, compare_layer)

    # main
    arcpy.SetProgressor("default", "Gettin' Loaded.......")
    infile = arcpy.GetParameterAsText(0)
    layer = "Temp"
    layer2 = "Temp2"
    query = arcpy.GetParameterAsText(1)
    infile2 = arcpy.GetParameterAsText(2)
    outfile = arcpy.GetParameterAsText(3)
    outtable = arcpy.GetParameterAsText(4)
    
    layer_create(infile, layer, query)
    layer_create(infile2, layer2, '')
    arcpy.SetProgressorPosition()
    arcpy.SetProgressorLabel("Who's selecting?  I'm selecting.")
    select_features(layer2, 'within', layer)
    make_feature(layer2, outfile)
    make_table(layer2, outtable)
    
    arcpy.SetProgressorPosition()
    arcpy.SetProgressorLabel("Cleaning up!")
    
    arcpy.Delete_management(layer)
    arcpy.Delete_management(layer2)
    
    arcpy.SetProgressorPosition()
    arcpy.SetProgressorLabel("Done!")
    
    arcpy.AddMessage(layer + " is now the feature class: " + outfile)
    arcpy.AddMessage(layer + " is now the table: " + outtable)
    
    arcpy.ResetProgressor()

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
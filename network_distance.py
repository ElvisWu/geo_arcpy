# Network Distance Tool
#
# A utility for measuring and creating distance buffers built around points
# using a street network dataset
#
# Arguments
#
# 0 - Network Dataset
#
# 1 - Point file
#
# 2 - Distance
#
# 3 - Outfile
#
# Created: 04/2012
# Aaron Burgess
# Using Python 2.6 (with arcpy)
#####################################################################################
# import modules
import arcpy, sys, traceback, os

# arguments
net_set = arcpy.GetParameterAsText(0) # replace everything after = with your network dataset if you do not want to add this to the arc toolbox
points = arcpy.GetParameterAsText(1) # replace everything after = with the point file you want
dist = arcpy.GetParameterAsText(2) # replace everything after = with the distance you want but make sure it looks like this "300"
outfile = arcpy.GetParameterAsText(3) # replace everything after = with the location you want to save the output layer

# set environment
arcpy.env.workspace = "CURRENT"

# global variables
temp = "temp"
outlayer, unused = os.path.split(net_set)
fin_layer = outlayer + "/"+unused+"_"+dist+".lyr" # No longer needed but kept for my own purposes

# functions
try:
    # Begin Progressor bar...
    arcpy.SetProgressor("step","Beginning Build...", 0, 4, 1)
    # Make sure Network Extension is present, will return explained error if extension is not available
    arcpy.CheckOutExtension("Network")
    
    # Create a Service Area Layer
    arcpy.MakeServiceAreaLayer_na(net_set, temp, "Length", "TRAVEL_FROM", dist, "SIMPLE_POLYS", "NO_MERGE")
    arcpy.SetProgressorLabel("Adding Locations...")
    arcpy.SetProgressorPosition(1)
    # Add Locations to Network Layer for Buffers
    arcpy.AddLocations_na(temp, "Facilities", points, "", "")
    arcpy.SetProgressorLabel("Solving...")
    arcpy.SetProgressorPosition(2)
    # Create buffers based on line distance from specified points
    arcpy.Solve_na(temp)
    arcpy.SetProgressorLabel("Creating Layer...")
    arcpy.SetProgressorPosition(3)
    # check to see if the output file already exists, WILL DELETE ANY PRE-EXISTING FILE WITH THE SAME NAME!!
    if arcpy.Exists(outfile):
        arcpy.Delete_management(outfile)
    # Save layer file
    arcpy.SaveToLayerFile_management(temp, outfile, "RELATIVE")
    arcpy.SetProgressorPosition(4)
    arcpy.ResetProgressor()
    
except:
    # Begin Error Handling
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
    # Clean up unnecessary files
    del temp
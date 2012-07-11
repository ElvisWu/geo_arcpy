# Clears all features from the default geodatabase
#
# Designed to clean up unintended features and more saved
# to the a default geodatabase that the Arc set rather than the user
#
# Aaron Burgess
# Created: 04/2012
# Python 2.6.8
###############################################################################
# import modules
import arcpy, sys, traceback

try:
    arcpy.env.workspace = r"C:\Users\Aaron\Documents\ArcGIS\Default.gdb" # set to your default GDB path
    arcpy.AddMessage("Your default geodatabase will soon be sparkling clean")
    # Remove all feature classes
    for items in arcpy.ListFeatureClasses():
        arcpy.Delete_management(items)
    # Remove all tables
    for items in arcpy.ListTables():
        arcpy.Delete_management(items)
    # Remove all rasters
    for items in arcpy.ListRasters():
        arcpy.Delete_management(items)
    arcpy.AddMessage("So fresh and so clean!!!")

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
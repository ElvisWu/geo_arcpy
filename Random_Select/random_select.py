# Randomizer
#
# Takes a given feature class, examines the total number of features
# and returns a random selection based on the percentage the user
# wants returned.  Additionally, specific criteria can be used
# regarding what observations or rows randomizer should look through.
#
# Arguments:
#
# 0 - Input feature class or shapefile
#
# 1 - Sample size as a percentage from the file
#
# 2 - SQL expression to select out variables (optional)
#
# 3 - Output feature class or shapefile
#
# Aaron Burgess
# Created: 02/06/2012
# Python 2.6 (arcpy module)
############################################################################
# import modules
import arcpy, sys, traceback, random, tempfile, shutil

# arguments
infile = arcpy.GetParameterAsText(0)
percent = arcpy.GetParameterAsText(1)
expression = arcpy.GetParameterAsText(2)
outfile = arcpy.GetParameterAsText(3)

# workspace
arcpy.env.workspace = "CURRENT"

# variables
temp_path = tempfile.mkdtemp()
temp = "temp"
sort = "Sort"
choice = "Choice"
counter = "Counter"
drop_fields = ["Sort", "Choice"]

# main
try:
    arcpy.SetProgressor("step", "Setting up data", 0, 5, 1)
    
    # Check to see if the temporary layer exists, replace it if it does
    if arcpy.Exists(temp):
        arcpy.Delete_management(temp)
        
    # check to see if expression (an SQL expression) has a value and create layer accordingly
    if expression != "":
        arcpy.MakeFeatureLayer_management(infile, temp, expression)
    elif expression == "":
        arcpy.MakeFeatureLayer_management(infile, temp)
        
    # add fields "Sort" and "Choice."  Each observation will be assigned a random integer
    # in the "Sort" field.  Rows are then sorted by "Sort" ascending and auto-increment
    # integers are added to the "Choice" field
    arcpy.AddField_management(temp, sort, "LONG")
    arcpy.AddField_management(temp, choice, "LONG")
    arcpy.SetProgressorLabel("Generating Random Values")
    arcpy.SetProgressorPosition(1)
    srows = arcpy.UpdateCursor(temp)
    for srow in srows:
        wacky = random.randint(0,100)
        srow.sort = wacky
        srows.updateRow(srow)
    arcpy.SetProgressorLabel("Sorting")
    arcpy.SetProgressorPosition(2)
    lrows = arcpy.UpdateCursor(temp,"","","", sort + " A")
    count = 0
    for lrow in lrows:
        lrow.choice = count
        lrows.updateRow(lrow)
        count += 1
   
    # release cursors    
    del srow
    del srows
    del lrow
    del lrows
    
    # count total number of rows in layer
    observations = int(arcpy.GetCount_management(temp).getOutput(0))
    
    # create integer equal to "number of rows" times percent return desired
    selection = int(observations*float(percent))+1
    
    # Select all rows where the "Choice" value is less than or equal to above equation 
    # and create a new feature class or shapefile
    expression2 = "\"Choice\" < " + str(selection)
    arcpy.SetProgressorLabel("Creating new feature")
    arcpy.SetProgressorPosition(3)
    arcpy.Select_analysis(temp, outfile, expression2)
    
    # Delete added fields from both input file and output file
    arcpy.SetProgressorLabel("Cleaning Up")
    arcpy.SetProgressorPosition(4)
    arcpy.DeleteField_management(outfile, drop_fields)
    arcpy.DeleteField_management(infile, drop_fields)

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
    # release parsing cursors and reset progressor bar
    arcpy.SetProgressorPosition(5)
    arcpy.Delete_management(temp)
    arcpy.ResetProgressor()
    shutil.rmtree(temp_path)
# Calculate percent of area of polygons inside a polygon

import arcpy, os, sys, traceback, shutil, tempfile

# user inputs
inFeature = arcpy.GetParameterAsText(0)
areaFeatures = arcpy.GetParameterAsText(1)
fieldNames = arcpy.GetParameterAsText(2)

field_split = fieldNames.split(",")
fielders = []
for field in field_split:
    fielders.append(field)
tempDir = tempfile.mkdtemp()
tempName = "temp.shp"
tempFile = tempDir+"temp.shp"
tempFile2 = tempDir+"temp_int.shp"

# functions
class PercentArea(object):
     
    def __init__(self, infile, *args):
        self.fields = []
        self.infile = infile
        self.inFeatures = [self.infile]
        for arg in args:
            self.fields.append(arg)
        for field in self.fields:
            arcpy.AddField_management(infile, field, "DOUBLE")
        arcpy.AddField_management(infile, "unique", "LONG")
        srows = arcpy.UpdateCursor(infile)
        count = 0
        for srow in srows:
            srow.unique = count
            srows.updateRow(srow)
            count += 1
        del srow
        del srows
            
    def sect_and_dissolve(self, *args):
        for arg in args:
            if arcpy.Exists(tempFile, tempFile2, "temp_lyr"):
                arcpy.Delete_management(tempFile, tempFile2, "temp_lyr")
            self.inFeatures.append(arg)
            arcpy.Intersect_analysis(self.inFeatures, tempFile)
            self.inFeatures.remove(arg)
            arcpy.Dissolve_management(tempFile, tempFile2, "unique", "Shape_Area SUM", "MULTI_PART", "DISSOLVE_LINES")
            arcpy.MakeFeatureLayer_management(tempFile2, "temp_lyr")
            arcpy.JoinField_management(self.infile, "unique", "temp_lyr", "unique", "SUM_Shape_Area;unique")
            srows = arcpy.UpdateCursor(self.infile)
            count2 = 0
            for srow in srows:
                sum_area = srow.getValue("SUM_Shape_Area")
                area = srow.getValue("Shape_Area")
                result = float(sum_area)/float(area)
                fieldName = self.fields[count2]
                srow.fieldName = result
                srows.updateRow(srow)
                count2 += 1
        del srow
        del srows
        arcpy.DeleteField_management(self.infile, "unique", "SUM_Shape_Area")
        
# main
try:
    cookie_cutter = PercentArea(inFeature, fielders)
    cookie_cutter.sect_and_dissolve(areaFeatures)
    
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
    shutil.rmtree(tempDir)
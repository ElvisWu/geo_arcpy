# Calculate percent of area of polygons inside a polygon

from __future__ import division
import arcpy, os, sys, traceback, shutil, tempfile


# user inputs
inFeature = arcpy.GetParameterAsText(0)
areaFeatures = arcpy.GetParameterAsText(1)
fieldNames = arcpy.GetParameter(2)

# functions
class Within_Area_Calc(object):
    
    def __init__(self, infile, fields):
        self.infile = infile
        self.fields = fields
        arcpy.AddField_management(self.infile, self.fields, "DOUBLE")
        arcpy.AddField_management(self.infile, "unique", "LONG")
        srows = arcpy.UpdateCursor(self.infile)
        count = 0
        for srow in srows:
            srow.unique = count
            srows.updateRow(srow)
            count += 1
        del srow
        del srows
                
    def sect_and_dissolve(self, sub_features):
        feat_list = [self.infile, sub_features]
        temp_list = ["temp", "temp_int"]
        try:
            for item in temp_list:
                if arcpy.Exists(item):
                    arcpy.Delete_management(item)
            arcpy.Intersect_analysis(feat_list, "temp")
            arcpy.Dissolve_management("temp", "temp_int", "unique", "Shape_Area SUM", "MULTI_PART", "DISSOLVE_LINES")
            arcpy.MakeFeatureLayer_management("temp_int", "temp_lyr")
            arcpy.JoinField_management(self.infile, "unique", "temp_lyr", "unique", "SUM_Shape_Area;unique")
            srows = arcpy.UpdateCursor(self.infile)
            for srow in srows:
                try:
                    sum_area = srow.getValue("SUM_Shape_Area")
                    area = srow.getValue("Shape_Area")
                    result = sum_area/area
                    srow.setValue(self.fields, result)
                    srows.updateRow(srow)
                except(TypeError, NameError, ValueError, IOError):
                    pass
            del srow
            del srows
            fielddrop = ["unique","unique_1", "SUM_Shape_Area"]
            arcpy.DeleteField_management(self.infile, fielddrop)
        except(SyntaxError, NameError, ValueError, IOError):
            pass
    
# main
try:
    if __name__ == '__main__':
        Area_Calc = Within_Area_Calc(inFeature, fieldNames)
        Area_Calc.sect_and_dissolve(areaFeatures)
    
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

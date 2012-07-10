import arcpy
infile = arcpy.GetParameterAsText(0)
percent = arcpy.GetParameterAsText(1)
row_count = arcpy.GetParameterAsText(2)
def corky(temp1, number, counter):
    end_num = int(float(number)*int(counter))
    srows = arcpy.UpdateCursor(temp1)
    count = 0
    for srow in srows:
        if count > end_num:
            count = 0
        else:
            count += 1
        srow.Sort = int(count)
        srows.updateRow(srow)
    del srow
    del srows

corky(infile, percent, row_count)
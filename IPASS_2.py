# I-PASS
#
# Indianapolis Python Address Standardization System
#
# Program designed to clean and standardize address records using a series
# of protocols and validations
#
# Aaron Burgess
# Created: March 2012
# Using Python 2.6
#########################################################################################################
# import modules
import re, difflib, sys, string, traceback, arcpy

# Input Parameters
infile = arcpy.GetParameterAsText(0)
str_field = arcpy.GetParameterAsText(1)
city_field = arcpy.GetParameterAsText(2)
state_field = arcpy.GetParameterAsText(3)
zip_field = arcpy.GetParameterAsText(4)
outfile = arcpy.GetParameterAsText(5)

# class objects
class Prepare(object):
    def __init__(self, street, str_file1, str_file2, str_file3):
        self.street = street
        self.str_file1 = str_file1
        self.str_file2 = str_file2
        self.str_file3 = str_file3
    
    def clean(self):
        rep = re.sub(r'[^0-9A-Za-z]+', '', self.street)
        newer = rep.strip()
        str_prep = newer    
        if str_prep[0].isdigit():
            number = str_prep.split(" ", 1)
            str_num = ''.join(number[0])
        else:
            number = ''
            str_num = ''.join(number)
        street_prep = re.sub(r'[0-9]+','',str_prep)
        street2 = re.sub(r'\s+','', street_prep)
        str_final = street2.strip()
        clean_str = str_final
        correction = difflib.get_close_matches(clean_str, self.str_file1, 1, 0.7)
        correction2 = difflib.get_close_matches(clean_str, self.str_file2, 1, 0.7)
        correction3 = difflib.get_close_matches(clean_str, self.str_file3, 1, 0.7)
        match1 = ''.join(correction)
        match2 = ''.join(correction2)
        match3 = ''.join(correction3)
        if match1 != '':
            final_str = match1
            final = str_num + " " + final_str
            final2 = final.strip()
            return final2
        elif match1 == '' and match2 != '':
            self.final_str = match2
            final = str_num + " " + final_str
            final2 = final.strip()
            return final2
        elif match1 == '' and match2 == '' and match3 != '':
            self.final_str = match3
            final = str_num + " " + final_str
            final2 = final.strip()
            return final2
        else:
            return self.street
    
class Place(object):
    def __init__(self, city, state, zip_code):
        self.city = city
        self.state = state
        self.zipcode = zip_code
        
    def city(self):
        cities = ["INDIANAPOLIS", "BEECH GROVE", "SOUTHPORT", "SPEEDWAY", "LAWRENCE"]
        city_prep = re.sub(r'[^A-Z]+','', self.city)
        city_check = city_prep.strip()
        city_correct = difflib.get_close_matches(city_check, cities, 1, 0.6)
        final_city = ''.join(city_correct)
        return final_city
    
    def state(self):
        rep = re.sub(r'[^A-Z]+', '', self.state)
        newer = rep.strip()
        return newer
    
    def zip_clean(self):
        rep = re.sub(r'[^0-9]+', '', self.zipcode)
        newer = rep.strip()
        return newer
    
# main
try:
    f = open(outfile+".csv", 'wb')
    f.write("Orig_Add, Address_Clean, City_Clean, St_Clean, Zip_Clean,")
    f.write("\n")
    pass1 = open(r'C:\Users\Aaron\Desktop\ipass_check1.txt', 'rb')
    read1 = pass1.read()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        ender = check.append(matcher)
    pass1.close()
    pass2 = open(r'C:\Users\Aaron\Desktop\ipass_check2.txt', 'rb')
    read2 = pass2.read()
    splitter2 = read1.split(",")
    check2 = []
    for item in splitter2:
        matcher2 = ''.join(item)
        ender2 = check2.append(matcher2)
    pass2.close()
    pass3 = open(r'C:\Users\Aaron\Desktop\ipass_check3.txt', 'rb')
    read3 = pass3.read()
    splitter3 = read3.split(",")
    check3 = []
    for item in splitter3:
        matcher3 = ''.join(item)
        ender3 = check3.append(matcher3)
    pass3.close()
    srows = arcpy.UpdateCursor(infile)
    for srow in srows:
        streeter = srow.getValue(str_field)
        city_row = srow.getValue(city_field)
        st_row = srow.getValue(state_field)
        zip_row = srow.getValue(zip_field)
        f.write(streeter+",")
        starter = Prepare(streeter, check, check2, check3)
        add_match = starter.clean()
        f.write(add_match+",")
        place_match = Place(city_field, state_field, zip_field)
        city_match = Place.city()
        st_match = Place.state()
        zip_match = Place.zip_clean()
        f.write(city_match+", "+st_match+", "+zip_match+",")
        f.write("\n")
    f.close()
    del srow
    del srows

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
    
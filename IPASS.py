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
import re, difflib, sys, traceback, tempfile, shutil

# variables
temp_dir = tempfile.mkdtemp()

# class objects
class Prepare(object):
    def __init__(self, street, check, check1, check2):
        self.street = street
        self.check = check
        self.check1 = check1
        self.check2 = check2
        self.final2 = None
    
    def clean(self):
        first = re.escape(self.street)
        rep = re.sub(r'[^0-9A-Za-z]+', '', first)
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
        correction = difflib.get_close_matches(clean_str, self.check, 1, 0.6)
        match1 = ''.join(correction)
        correction2 = difflib.get_close_matches(clean_str, self.check1, 1, 0.6)
        match2 = ''.join(correction2)
        correction3 = difflib.get_close_matches(clean_str, self.check2, 1, 0.6)
        match3 = ''.join(correction3)
        if match1 != '':
            final_str = match1
            final = str_num + " " + final_str
            self.final2 = final.strip()
        elif match1 == '' and match2 != '':
            self.final_str = match2
            final = str_num + " " + final_str
            self.final2 = final.strip()
        elif match1 == '' and match2 == '' and match3 != '':
            self.final_str = match3
            final = str_num + " " + final_str
            self.final2 = final.strip()
        return self.final2
    
    def __str__(self):
        return self.final2
    
class Place(object):
    def __init__(self, city, state, zip_code):
        self.city = city
        self.state = state
        self.zipcode = zip_code
        
    def city(self):
        cities = ["INDIANAPOLIS", "BEECH GROVE", "SOUTHPORT", "SPEEDWAY", "LAWRENCE"]
        first = re.escape(self.city)
        city_prep = re.sub(r'[0-9]+','', first)
        city_check = city_prep.strip()
        city_correct = difflib.get_close_matches(city_check, cities, 1, 0.6)
        city_final = ''.join(city_correct)
        return city_final
    
    def state(self):
        first = re.escape(self.state)
        rep = re.sub(r'[^A-Z]+', '', first)
        newer = rep.strip()
        return newer
    
    def zip_clean(self):
        first = re.escape(self.zipcode)
        rep = re.sub(r'[^0-9]+', '', first)
        newer = rep.strip()
        return newer
    
# main
try:
    infile = raw_input("Please put in your file path: ")
    outfile = raw_input("Please put in your output path: ")
    pass1 = open(r'C:\Users\Aaron\Desktop\ipass_check1.txt', 'r')
    read1 = pass1.read()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        check.append(matcher)
    pass1.close()
    pass2 = open(r'C:\Users\Aaron\Desktop\ipass_check2.txt', 'r')
    read2 = pass2.read()
    splitter2 = read2.split(",")
    check2 = []
    for item in splitter2:
        matcher2 = ''.join(item)
        check2.append(matcher2)
    pass2.close()
    pass3 = open(r'C:\Users\Aaron\Desktop\ipass_check3.txt', 'r')
    read3 = pass3.read()
    splitter3 = read3.split(",")
    check3 = []
    for item in splitter3:
        matcher3 = ''.join(item)
        check3.append(matcher3)
    pass3.close()
    use = open(infile+".csv", 'rb')
    use2 = use.readlines()
    f = open(outfile+".csv", 'wb')
    f.write("Orig_Add, Address_Clean, City_Clean, St_Clean, Zip_Clean")
    f.write("\n")
    for i in use2:
        record = i.split(",")
        address = ''.join(record[0])
        city = ''.join(record[1])
        state = ''.join(record[2])
        zip_code = ''.join(record[3])
        add_clean = Prepare(address, check, check2, check3)
        final_add = add_clean.clean()
        place_clean = Place(city, state, zip_code)
        fin_city = place_clean.city()
        fin_state = place_clean.state()
        fin_zip = place_clean.zip_clean()
        f.write(address+","+final_add+","+fin_city+","+fin_state+","+fin_zip+","+"\n")
    use.close()
    f.close()  

except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = 'PYTHON ERRORS:\nTraceback Info:\n' + tbinfo + 'n\Error Info:\n'
finally:
    shutil.rmtree(temp_dir)
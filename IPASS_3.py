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
import re, difflib, sys, traceback

# Input Parameters
infile = r'C:\Users\Aaron\Desktop\trial_part2'
outfile = r'C:\Users\Aaron\Desktop\final_trial'

# class objects    
def clean(street):
    str_num = None
    first = re.escape(street)
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
    correction = difflib.get_close_matches(clean_str, check, 1, 0.7)
    correction2 = difflib.get_close_matches(clean_str, check2, 1, 0.7)
    correction3 = difflib.get_close_matches(clean_str, check3, 1, 0.7)
    match1 = ''.join(correction)
    match2 = ''.join(correction2)
    match3 = ''.join(correction3)
    if match1 != '':
        final_str = match1
        final = str_num + " " + final_str
        final2 = final.strip()
    elif match1 == '' and match2 != '':
        final_str = match2
        final = str_num + " " + final_str
        final2 = final.strip()
    elif match1 == '' and match2 == '' and match3 != '':
        final_str = match3
        final = str_num + " " + final_str
        final2 = final.strip()
    return final2
    
def city(city):
    cities = ["INDIANAPOLIS", "BEECH GROVE", "SOUTHPORT", "SPEEDWAY", "LAWRENCE"]
    city_prep = re.sub(r'[^A-Z]+','', city)
    city_check = city_prep.strip()
    city_correct = difflib.get_close_matches(city_check, cities, 1, 0.6)
    return city_correct

def state(state):
    rep = re.sub(r'[^A-Z]+', '', state)
    newer = rep.strip()
    return newer

def zip_clean(zip_code):
    rep = re.sub(r'[^0-9]+', '', zip_code)
    newer = rep.strip()
    return newer

# main
try:
    use = open(infile+".csv", 'rb')
    use2 = use.readlines()
    f = open(outfile+".csv", 'wb')
    f.write("Orig_Add, Address_Clean, City_Clean, St_Clean, Zip_Clean,")
    f.write("\n")
    pass1 = open(r'C:\Users\Aaron\Desktop\ipass_check1.txt', 'r')
    read1 = pass1.readline()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        ender = check.append(matcher)
    pass1.close()
    pass2 = open(r'C:\Users\Aaron\Desktop\ipass_check2.txt', 'r')
    read2 = pass2.readline()
    splitter2 = read2.split(",")
    check2 = []
    for item in splitter2:
        matcher2 = ''.join(item)
        ender2 = check2.append(matcher2)
    pass2.close()
    pass3 = open(r'C:\Users\Aaron\Desktop\ipass_check3.txt', 'r')
    read3 = pass3.readline()
    splitter3 = read3.split(",")
    check3 = []
    for item in splitter3:
        matcher3 = ''.join(item)
        ender3 = check3.append(matcher3)
    pass3.close()
    for line in use2:
        record = line.split(",")
        address = ''.join(record[0])
        city = ''.join(record[1])
        state = ''.join(record[2])
        zip_code = ''.join(record[3])
        final_add = clean(address)
        fin_city = city(city)
        fin_state = state(state)
        fin_zip = zip_clean(zip_code)
        f.write(address+","+final_add+","+fin_city+","+fin_state+","+fin_zip+","+"\n")
    use.close()
    f.close() 

except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = 'PYTHON ERRORS:\nTraceback Info:\n' + tbinfo + 'n\Error Info:\n'
    
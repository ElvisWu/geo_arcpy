#-------------------------------------------------------------------------------
# Name:        I-PASS (Next Generation)
# Purpose:     Extremely finite address standardization system for addresses
#              from Indianapolis, IN.  Standardizes addresses based on
#              probability of street occurrence, reference to zip code, and
#              converts common name locations to their respective address.
#              Additionally, I-PASS logs addresses for which it cannot match
#              which the user can call up and later add to the Indy area
#              address dictionaries.  NOTE: This is intended ONLY for
#              Indianapolis addresses and WILL NOT work on other areas.  A
#              project is currently underway to make this an interchangeable
#              system.
#
# Author:      Aaron
#
# Created:     06/06/2012
# Copyright:   (c) Aaron 2012
# Licence:     Aaron Burgess using Python 2.6.2 (using arcpy module)
#-------------------------------------------------------------------------------
# import modules
import arcpy, sys, os, traceback, re, difflib, string

# arguments
infile = arcpy.GetParameterAsText(0)
street = arcpy.GetParameterAsText(1)
city = arcpy.GetParameterAsText(2)
state = arcpy.GetParameterAsText(3)
zip_code = arcpy.GetParameterAsText(4)

# functions
def setup(infiles):
    arcpy.AddField_management(infiles, "street_cl", "TEXT", "", "", "254")
    arcpy.AddField_management(infiles, "add_clean1", "TEXT", "", "", "175")
    arcpy.AddField_management(infiles, "add_clean2", "TEXT", "", "", "175")
    arcpy.AddField_management(infiles, "add_clean3", "TEXT", "", "", "175")
    arcpy.AddField_management(infiles, "zip_street", "TEXT", "", "", "254")
    arcpy.AddField_management(infiles, "fin_address", "TEXT", "", "", "254")
    arcpy.AddField_management(infiles, "st_combo", "TEXT", "", "", "254")
    arcpy.AddField_management(infiles, "city_clean", "TEXT", "", "", "150")
    arcpy.AddField_management(infiles, "state_clean", "TEXT", "", "", "10")
    arcpy.AddField_management(infiles, "zip_clean", "TEXT", "", "", "20")
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        st_cl = srow.getValue(street)
        orig = re.escape(st_cl)
        rep = re.sub('[^0-9A-Za-z&\\/#\s]+', '', orig)
        rep2 = re.sub(r'(\bAPT\b|\bRM\b|\bLOT\b|\bSTE\b|\bSUITE\b|\bUNIT\b)(\s+)(\s[0-9A-Z]+|\s[A-Z]+|\s[0-9]+|[A-Z]|[0-9]+)', '', rep)
        newer = rep2.strip()
        rep3 = re.sub(r'(#[0-9A-Z]+|#[0-9]+|#\s[0-9]+|#[A-Z]+|#\s[A-Z]+)', '', newer)
        rep4 = re.sub(r'(\bAPT\b|\bRM\b|\bLOT\b|\bSTE\b|\bSUITE\b|\bUNIT\b|\bLOT\b|\bUNK\b|\bUNKNOWN\b)', '', rep3)
        newer2 = rep4.strip()
        fire = newer2.split(' ')
        if newer2 == '' or newer2 == "":
            newer2 = " "
        if newer2[0].isdigit() and len(fire)>1:
            number,str_add = newer2.split(' ', 1)
        if str_add == "PENN" or str_add == "PENN AVE" or str_add == "PENN ST":
            newer2 = number + " PENNSYLVANIA ST"
        elif str_add == "MLK" or str_add == "DR MLK" or str_add == "MLK DR" or str_add == "MLK JR" or str_add == "MLK JR DR":
            newer2 = number + " DR MARTIN LUTHER KING"
        elif str_add == "AJB" or str_add == "DR AJB" or str_add == "DR AJB DR":
            newer2 = number + " DR ANDREW J BROWN"
        if newer2 == '':
            srow.street_cl = " "
        else:
            srow.street_cl = newer2
        srows.updateRow(srow)
    del srow
    del srows

def address_check(infiles):
    pass1 = open(r'C:\Documents and Settings\aaburges\Desktop\ipass_docs\ipass_check1.txt', 'rb')
    read1 = pass1.readline()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        ender = check.append(matcher)
    pass1.close()
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        streeter = srow.getValue("street_cl")
        rep = re.sub(r'[^0-9A-Za-z\s]+', '', streeter)
        newer = rep.strip()
        str_prep = newer
        fire = str_prep.split(' ')
        if str_prep == '' or str_prep == "":
            str_prep = " "
        if str_prep[0].isdigit() and len(fire)>1:
            number,str_add = str_prep.split(' ', 1)
            str_num = ''.join(number)
            streeter = ''.join(str_add)
        else:
            str_num = ''
            streeter = str_prep
        if streeter[0].isdigit:
            street_prep = streeter
        else:
            street_prep = re.sub(r'[0-9]+','',streeter)
        street2 = re.sub(r'\s+','', street_prep)
        clean_str= street2.strip()
        correction = difflib.get_close_matches(clean_str, check, 1, 0.6)
        match1 = ''.join(correction)
        final_match = str_num + " " + match1
        add1 = final_match.strip()
        if add1[0:].isdigit() or add1 == "":
            srow.add_clean1 = ''
        else:
            srow.add_clean1 = add1
        srows.updateRow(srow)
    del srow
    del srows

def address_check2(infiles):
    pass1 = open(r'C:\Documents and Settings\aaburges\Desktop\ipass_docs\ipass_check2.txt', 'rb')
    read1 = pass1.readline()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        ender = check.append(matcher)
    pass1.close()
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        streeter = srow.getValue("street_cl")
        rep = re.sub(r'[^0-9A-Za-z\s]+', '', streeter)
        newer = rep.strip()
        str_prep = newer
        fire = str_prep.split(' ')
        if str_prep == '' or str_prep == "":
            str_prep = " "
        if str_prep[0].isdigit() and len(fire)>1:
            number,str_add = str_prep.split(' ', 1)
            str_num = ''.join(number)
            streeter = ''.join(str_add)
        else:
            str_num = ''
            streeter = str_prep
        if streeter[0].isdigit:
            street_prep = streeter
        else:
            street_prep = re.sub(r'[0-9]+','',streeter)
        street2 = re.sub(r'\s+','', street_prep)
        clean_str= street2.strip()
        correction = difflib.get_close_matches(clean_str, check, 1, 0.6)
        match1 = ''.join(correction)
        final_match = str_num + " " + match1
        add1 = final_match.strip()
        if add1[0:].isdigit() or add1 == "":
            srow.add_clean2 = ''
        else:
            srow.add_clean2 = add1
        srows.updateRow(srow)
    del srow
    del srows

def address_check3(infiles):
    pass1 = open(r'C:\Documents and Settings\aaburges\Desktop\ipass_docs\ipass_check3.txt', 'rb')
    read1 = pass1.readline()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        ender = check.append(matcher)
    pass1.close()
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        streeter = srow.getValue("street_cl")
        rep = re.sub(r'[^0-9A-Za-z\s]+', '', streeter)
        newer = rep.strip()
        str_prep = newer
        fire = str_prep.split(' ')
        if str_prep == '' or str_prep == "":
            str_prep = " "
        if str_prep[0].isdigit() and len(fire)>1:
            number,str_add = str_prep.split(' ', 1)
            str_num = ''.join(number)
            streeter = ''.join(str_add)
        else:
            str_num = ''
            streeter = str_prep
        if streeter[0].isdigit:
            street_prep = streeter
        else:
            street_prep = re.sub(r'[0-9]+','',streeter)
        street2 = re.sub(r'\s+','', street_prep)
        clean_str= street2.strip()
        correction = difflib.get_close_matches(clean_str, check, 1, 0.6)
        match1 = ''.join(correction)
        final_match = str_num + " " + match1
        add1 = final_match.strip()
        if add1[0:].isdigit() or add1 == "":
            srow.add_clean3 = ''
        else:
            srow.add_clean3 = add1
        srows.updateRow(srow)
    del srow
    del srows

def city_clean(infiles):
    cities = ["INDIANAPOLIS", "BEECH GROVE", "SOUTHPORT", "SPEEDWAY", "LAWRENCE"]
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        town = srow.getValue(city)
        stater = srow.getValue(state)
        zipper = srow.getValue(zip_code)
        first = re.escape(town)
        city_prep = re.sub(r'[^A-Z]+','',first)
        city_check = city_prep.strip()
        city_correct = difflib.get_close_matches(city_check, cities, 1, 0.6)
        match = ''.join(city_correct)
        srow.city_clean = match
        second = re.escape(stater)
        rep = re.sub(r'[^A-Z]','',second)
        newer = rep.strip()
        srow.state_clean = newer
        third = re.escape(zipper)
        rep2 = re.sub(r'[^0-9]+','',third)
        newer2 = rep2.strip()
        srow.zip_clean = newer2[0:5]
        srows.updateRow(srow)
    del srow
    del srows

def combo(infiles):
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        streeter = srow.getValue("street_cl")
        zipper = srow.getValue("zip_clean")
        result = streeter + " " + zipper
        srow.st_combo = result
        srows.updateRow(srow)
    del srow
    del srows

def zip_to_street(infiles):
    pass1 = open(r'C:\Documents and Settings\aaburges\Desktop\ipass_docs\zip_dict.txt', 'rb')
    read1 = pass1.readline()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        ender = check.append(matcher)
    pass1.close()
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        streeter = srow.getValue("st_combo")
        rep = re.sub(r'[^0-9A-Za-z\s]+', '', streeter)
        newer = rep.strip()
        str_prep = newer
        fire = str_prep.split(' ')
        if str_prep == '' or str_prep == "":
            str_prep = " "
        if str_prep[0].isdigit() and len(fire)>1:
            number,str_add = str_prep.split(' ', 1)
            str_num = ''.join(number)
            streeter = ''.join(str_add)
        else:
            str_num = ''
            streeter = str_prep
        if streeter[0].isdigit:
            street_prep = streeter
        else:
            street_prep = re.sub(r'[0-9]+','',streeter)
        street2 = re.sub(r'\s+','', street_prep)
        clean_str= street2.strip()
        correction = difflib.get_close_matches(clean_str, check, 1, 0.6)
        match1 = ''.join(correction)
        final_match = str_num + " " + match1
        add1 = final_match.strip()
        add2 = add1[:-6]
        if add2[0:].isdigit() or add2 == "":
            srow.zip_street = ''
        else:
            srow.zip_street = add2
        srows.updateRow(srow)
    del srow
    del srows

def add_select(infiles):
    f = open('C:\\Documents and Settings\\aaburges\\Desktop\\ipass_docs\\missing_log.txt', 'wb')
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        streeter2 = srow.getValue("street_cl")
        street1 = srow.getValue("add_clean1")
        street2 = srow.getValue("add_clean2")
        street3 = srow.getValue("add_clean3")
        street4 = srow.getValue("zip_street")
        streeter = []
        streeter.append(street1)
        streeter.append(street2)
        streeter.append(street3)
        streeter.append(street4)
        final = difflib.get_close_matches(streeter2, streeter, 1, 0.7)
        final2 = ''.join(final)
        if final2 != '':
            srow.fin_address = final2
        else:
            f.write(streeter2+",")
            srow.fin_address = streeter2
        srows.updateRow(srow)
    del srow
    del srows

def finale(infiles):
    f = open('C:\\Documents and Settings\\aaburges\\Desktop\\ipass_docs\\unique.txt', 'rb')
    read2 = f.readline()
    diction = {}
    splitter = read2.split(",")
    for item in splitter:
        key, value = item.split(":")
        diction[key] = value
    f.close()
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        streets = srow.getValue("fin_address")
        if streets in diction:
            srow.fin_address = diction[street]
        srows.updateRow(srow)
    arcpy.DeleteField_management(infiles, "street_cl;st_combo;add_clean1;add_clean2;add_clean3;zip_street")
    del srow
    del srows

try:
    setup(infile)
    address_check(infile)
    address_check2(infile)
    address_check3(infile)
    city_clean(infile)
    combo(infile)
    zip_to_street(infile)
    add_select(infile)
    finale(infile)

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
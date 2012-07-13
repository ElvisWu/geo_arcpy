#-------------------------------------------------------------------------------
# Name:        I-PASS (Next Generation)
# Purpose:     I-PASS is an address standardization program specific to Marion County, IN.  The
#              program functions by initialing cleaning addresses of secondary markers such as
#              apartments, lots, etc and irregular characters while cleaning up common vernacular
#              issues such as MLK for Martin Luther King or Penn for Pennsylvania.  The program then
#              uses a weighted system of existing street segments in Indianapolis to determine
#              three categories: (1) most commonly occurring street segments, (2) moderately
#              occurring street segments and (3) those segments with the least amount of occurrences
#
# Author:      Aaron Burgess
#
# Created:     06/06/2012
# Copyright:   (c) Aaron 2012
# Licence:     To ill
#-------------------------------------------------------------------------------
# import modules
import arcpy, sys, os, traceback, re, difflib, string

# arguments
infile = arcpy.GetParameterAsText(0)
street = arcpy.GetParameterAsText(1)
city = arcpy.GetParameterAsText(2)
state = arcpy.GetParameterAsText(3)
zip_code = arcpy.GetParameterAsText(4)

# globals
cities = ["INDIANAPOLIS", "BEECH GROVE", "SOUTHPORT", "SPEEDWAY", "LAWRENCE"]

# functions
def setup(infiles):
    """Setups the given table for processing by adding fields.  'setup' then cleans the original address field by removing irregular characters,
    secondary addresses, and fixes colloquial misspellings."""
    arcpy.AddField_management(infiles, "street_cl", "TEXT", "", "", "254")    # add temp and final fields for calculation
    arcpy.AddField_management(infiles, "add_clean1", "TEXT", "", "", "175")
    arcpy.AddField_management(infiles, "add_clean2", "TEXT", "", "", "175")
    arcpy.AddField_management(infiles, "add_clean3", "TEXT", "", "", "175")
    arcpy.AddField_management(infiles, "zip_street", "TEXT", "", "", "254")
    arcpy.AddField_management(infiles, "fin_address", "TEXT", "", "", "254")
    arcpy.AddField_management(infiles, "st_combo", "TEXT", "", "", "254")
    arcpy.AddField_management(infiles, "city_clean", "TEXT", "", "", "254")
    arcpy.AddField_management(infiles, "state_clean", "TEXT", "", "", "30")
    arcpy.AddField_management(infiles, "zip_clean", "TEXT", "", "", "20")
    # begin parsing observations using a row cursor
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        if srow.getValue(street) == None:  
            # Check the address field for null values to avoid traceback fail
            srow.street_cl = ' '
        else:
            # If address field is not null then begin
            st_cl = srow.getValue(street)
            orig = re.escape(st_cl)  # Detect escape characters
            orig2 = orig.upper()     # Make address field uppercase
            # Begin standardizing intersections by replacing and, /, etc. with & only
            # then eliminate secondary addresses and numbers
            early = re.sub(r'/|&|\bAnd\b|\band\b|\bAND\b',' & ',orig2)
            rep = re.sub('[^0-9A-Za-z&\\/#\s]+', '', early)
            rep2 = re.sub(r'(\bAPT\b|\bRM\b|\bLOT\b|\bSTE\b|\bSUITE\b|\bUNIT\b)(\s+)(\s[0-9A-Z]+|\s[A-Z]+|\s[0-9]+|[A-Z]|[0-9]+)', '', rep)
            newer = rep2.strip()
            rep3 = re.sub(r'(#[0-9A-Z]+|#[0-9]+|#\s[0-9]+|#[A-Z]+|#\s[A-Z]+)', '', newer)
            rep4 = re.sub(r'(\bAPT\b|\bRM\b|\bLOT\b|\bSTE\b|\bSUITE\b|\bUNIT\b|\bLOT\b|\bUNK\b|\bUNKNOWN\b|\b1/2\b)', '', rep3)
            rep5 = re.sub(r'\s+', ' ',rep4)
            newer2 = rep5.strip()
            # split the cleaned address at the spaces, check if an address exists at all, then check to see if the first
            # character group in the address is numeric and there is more than one character group (e.g. the difference between '123 College Ave' and simply 'College'
            fire = newer2.split(' ')
            if newer2 == '' or newer2 == "":
                newer2 = " "
            if newer2[0].isdigit() and len(fire)>1:
                number,str_add = newer2.split(' ', 1)
                number = re.sub(r'[^0-9]+', '', number)  # retain only numbers in the street address number
            # Check if 'East', 'West', 'South' or 'North' exist in the address and that the address is long enough that the aforementioned is most likely
            # a pre-direction and not a road name; example: EAST WASHINGTON ST is > 7 characters and East is clearly a direction but East St is not > 7 and
            # should not be shortened
            if "EAST" in str_add and len(str_add)>7:
                rep_east = re.sub(r'\bEAST\b', 'E', str_add)
                newer2 = number + " " + rep_east
            elif "WEST" in str_add and len(str_add)>7:
                rep_west = re.sub(r'\bWEST\b', 'W', str_add)
                newer2 = number + " " + rep_west
            elif "NORTH" in str_add and len(str_add)>8:
                rep_north = re.sub(r'\bNORTH\b', 'N', str_add)
                newer2 = number + " " + rep_north
            elif "SOUTH" in str_add and len(str_add)>8:
                rep_south = re.sub(r'\bSOUTH\b', 'S', str_add)
                newer2 = number + " " + rep_south
            # Check for colloquial shortenings common to Indianapolis and correct them
            if str_add == "PENN" or str_add == "PENN AVE" or str_add == "PENN ST":
                newer2 = number + " PENNSYLVANIA ST"
            elif str_add == "MLK" or str_add == "DR MLK" or str_add == "MLK DR" or str_add == "MLK JR" or str_add == "MLK JR DR":
                newer2 = number + " DR MARTIN LUTHER KING DR"
            elif str_add == "AJB" or str_add == "DR AJB" or str_add == "DR AJB DR":
                newer2 = number + " DR A J BROWN AVE"
            # if the end result is blank, then return no value; otherwise return the cleaned address
            if newer2 == '':
                srow.street_cl = " "
            else:
                srow.street_cl = newer2
        # update the given row
        arcpy.AddMessage("Cleaned to: "+newer2)
        srows.updateRow(srow)
    # delete the cursor for this function
    del srow
    del srows

def address_check(infiles):
    """Checks the cleaned address against the most commonly occurring streets in Indianapolis.  Checks intersections as well."""
    pass1 = open(r'C:\Documents and Settings\aaburges\Desktop\ipass_docs\ipass_check1.txt', 'rb')  # load the text file featuring the most commonly occurring roads in Indianapolis, turn into a list and close the text file
    read1 = pass1.readline()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        check.append(matcher)
    pass1.close()
    # Create a cursor to examine each row 
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        if srow.getValue("street_cl") == ' ':    # if the value in field "street_cl" is blank then return a blank value and stop
            srow.add_clean1 = ' '
        else:
            # Remove all spaces from the cleaned address and retain only alphanumerics and '&' for intersections
            streeter = srow.getValue("street_cl")
            rep = re.sub(r'[^0-9A-Za-z&\s/]+', '', streeter)
            newer = rep.strip()
            str_prep = newer.upper()  # ensure the value is uppercase
            # split the value from "street_cl" at spaces
            fire = str_prep.split(' ')
            # if "street_cl" is blank then return a blank value
            if str_prep == '' or str_prep == "":
                str_prep = " "
            # if "&" exists in "street_cl" then an intersection is present, so split the address at '&' and place the road names
            # that occur before the '&' in variable road1 and place that which comes after '&' in road2
            if "&" in str_prep:
                cross1, cross2 = str_prep.split("&",1)
                str_prep = " "
                road1 = ''.join(cross1)
                road2 = ''.join(cross2)
            # check to see if the address has a street number and temporarily split into a seperate variable if present, else the 
            # separate variable is fillded with a blank value
            if str_prep[0].isdigit() and len(fire)>1:
                number,str_add = str_prep.split(' ', 1)
                str_num = ''.join(number)
                streeter = ''.join(str_add)
            else:
                str_num = ''
                streeter = str_prep
            # ensure the assumed street name is not numeric
            if streeter[0].isdigit:
                street_prep = streeter
            else:
                street_prep = re.sub(r'[0-9]+','',streeter)
            # if a street name value is present then ensure there are no spaces and check against the list of the most commonly
            # occurring street names (by segment) in Indianapolis using the difflib module (essentially comparable to Levenshtein distance.)
            # if a match occurs at or greater than the threshold of 0.7, combine the street number with the match and return the value
            if street_prep != " ":
                street2 = re.sub(r'\s+','', street_prep)
                clean_str= street2.strip()
                correction = difflib.get_close_matches(clean_str, check, 1, 0.7)
                match1 = ''.join(correction)
                final_match = str_num + " " + match1
                add1 = final_match.strip()
                add2 = re.sub(r'\s+', ' ', add1)
            # if variables road1 and road2 hold a value then you have an intersection.  Clean both variables like previous to determine
            # whether 'EAST' is a direction or a street name.
            elif road1 != '' and road2 != '':
                if "EAST" in road1 and len(road1)>7:
                    road1 = re.sub(r'\bEAST\b', 'E', road1)
                elif "WEST" in road1 and len(road1)>7:
                    road1 = re.sub(r'\bWEST\b', 'W', road1)
                elif "NORTH" in road1 and len(road1)>8:
                    road1 = re.sub(r'\bNORTH\b', 'N', road1)
                elif "SOUTH" in road1 and len(road1)>8:
                    road1 = re.sub(r'\bSOUTH\b', 'S', road1)
                route1 = re.sub(r'\s+','', road1)
                if "EAST" in road2 and len(road1)>7:
                    road2 = re.sub(r'\bEAST\b', 'E', road2)
                elif "WEST" in road2 and len(road1)>7:
                    road2 = re.sub(r'\bWEST\b', 'W', road2)
                elif "NORTH" in road2 and len(road1)>8:
                    road1 = re.sub(r'\bNORTH\b', 'N', road2)
                elif "SOUTH" in road2 and len(road1)>8:
                    road1 = re.sub(r'\bSOUTH\b', 'S', road2)
                route2 = re.sub(r'\s+','', road2)
                clean_road1 = route1.strip()
                clean_road2 = route2.strip()
                # check each road invidiually against the list of commonly occurring roads in Indianapolis
                correction = difflib.get_close_matches(clean_road1, check, 1, 0.7)
                correction2 = difflib.get_close_matches(clean_road2, check, 1, 0.7)
                match1 = ''.join(correction)
                match2 = ''.join(correction2)
                # if road1 has no match but road2 does, return the original road1 value and combine with the road2 match
                if match1 == '' and match2 != '':
                    final_match = road1 + " & " + match2
                # if road1 has a match but road2 does not, return the road1 match and combine with the original road2 value
                elif match1 != '' and match2 == '':
                    final_match = match1 + " & " + road2
                # if neither road1 or road2 return a match then assign a blank as the returned value
                elif match1 == '' and match2 == '':
                    final_match = ""
                # otherwise combine both matches
                else:
                    final_match = match1 + " & " + match2
                add1 = re.sub(r'\s+', ' ',final_match)
                add2 = add1.strip()
            # if there is no street name value at all then return a blank
            elif street_prep == " ":
                add2 = ""
            # if there is only a numeric group or a no value, then return a blank
            if add1[0:].isdigit() or add1 == "":
                srow.add_clean1 = ''
            # otherwise return the matched value for the most commonly occurring streets in Indianapolis
            else:
                arcpy.AddMessage("Probable match: "+add2)
                srow.add_clean1 = add2
        # update the given row
        srows.updateRow(srow)
    # delete the cursor for this function
    del srow
    del srows

def address_check2(infiles):
    """Checks the cleaned address against the moderately occurring streets in Indianapolis.  Checks intersections as well."""
    pass1 = open(r'C:\Documents and Settings\aaburges\Desktop\ipass_docs\ipass_check2.txt', 'rb')
    read1 = pass1.readline()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        check.append(matcher)
    pass1.close()
    # Create a cursor to examine each row 
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        if srow.getValue("street_cl") == ' ':    # if the value in field "street_cl" is blank then return a blank value and stop
            srow.add_clean2 = ' '
        else:
            streeter = srow.getValue("street_cl")
            rep = re.sub(r'[^0-9A-Za-z&\s/]+', '', streeter)
            newer = rep.strip()
            str_prep = newer.upper()
            fire = str_prep.split(' ')
            if str_prep == '' or str_prep == "":
                str_prep = " "
            if "&" in str_prep:
                cross1, cross2 = str_prep.split("&",1)
                str_prep = " "
                road1 = ''.join(cross1)
                road2 = ''.join(cross2)
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
            if street_prep != " ":
                street2 = re.sub(r'\s+','', street_prep)
                clean_str= street2.strip()
                correction = difflib.get_close_matches(clean_str, check, 1, 0.7)
                match1 = ''.join(correction)
                final_match = str_num + " " + match1
                add1 = final_match.strip()
                add2 = re.sub(r'\s+', ' ', add1)
            elif road1 != '' and road2 != '':
                if "EAST" in road1 and len(road1)>7:
                    road1 = re.sub(r'\bEAST\b', 'E', road1)
                elif "WEST" in road1 and len(road1)>7:
                    road1 = re.sub(r'\bWEST\b', 'W', road1)
                elif "NORTH" in road1 and len(road1)>8:
                    road1 = re.sub(r'\bNORTH\b', 'N', road1)
                elif "SOUTH" in road1 and len(road1)>8:
                    road1 = re.sub(r'\bSOUTH\b', 'S', road1)
                route1 = re.sub(r'\s+','', road1)
                if "EAST" in road2 and len(road1)>7:
                    road2 = re.sub(r'\bEAST\b', 'E', road2)
                elif "WEST" in road2 and len(road1)>7:
                    road2 = re.sub(r'\bWEST\b', 'W', road2)
                elif "NORTH" in road2 and len(road1)>8:
                    road1 = re.sub(r'\bNORTH\b', 'N', road2)
                elif "SOUTH" in road2 and len(road1)>8:
                    road1 = re.sub(r'\bSOUTH\b', 'S', road2)
                route2 = re.sub(r'\s+','', road2)
                clean_road1 = route1.strip()
                clean_road2 = route2.strip()
                correction = difflib.get_close_matches(clean_road1, check, 1, 0.7)
                correction2 = difflib.get_close_matches(clean_road2, check, 1, 0.7)
                match1 = ''.join(correction)
                match2 = ''.join(correction2)
                if match1 == '' and match2 != '':
                    final_match = road1 + " & " + match2
                elif match1 != '' and match2 == '':
                    final_match = match1 + " & " + road2
                elif match1 == '' and match2 == '':
                    final_match = ""
                else:
                    final_match = match1 + " & " + match2
                add1 = re.sub(r'\s+', ' ',final_match)
                add2 = add1.strip()
            elif street_prep == " ":
                add2 = ""
            if add1[0:].isdigit() or add1 == "":
                srow.add_clean2 = ''
            else:
                arcpy.AddMessage("Probable match: "+add2)
                srow.add_clean2 = add2
        srows.updateRow(srow)
    del srow
    del srows

def address_check3(infiles):
    """Checks the cleaned address against the least common streets in Indianapolis.  Checks intersections as well."""
    pass1 = open(r'C:\Documents and Settings\aaburges\Desktop\ipass_docs\ipass_check3.txt', 'rb')
    read1 = pass1.readline()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        check.append(matcher)
    pass1.close()
    # Create a cursor to examine each row 
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        if srow.getValue("street_cl") == ' ':
            srow.add_clean3 = ' '
        else:
            streeter = srow.getValue("street_cl")
            rep = re.sub(r'[^0-9A-Za-z&\s/]+', '', streeter)
            newer = rep.strip()
            str_prep = newer.upper()
            fire = str_prep.split(' ')
            if str_prep == '' or str_prep == "":
                str_prep = " "
            if "&" in str_prep:
                cross1, cross2 = str_prep.split("&",1)
                str_prep = " "
                road1 = ''.join(cross1)
                road2 = ''.join(cross2)
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
            if street_prep != " ":
                street2 = re.sub(r'\s+','', street_prep)
                clean_str= street2.strip()
                correction = difflib.get_close_matches(clean_str, check, 1, 0.7)
                match1 = ''.join(correction)
                final_match = str_num + " " + match1
                add1 = final_match.strip()
                add2 = re.sub(r'\s+', ' ', add1)
            elif road1 != '' and road2 != '':
                if "EAST" in road1 and len(road1)>7:
                    road1 = re.sub(r'\bEAST\b', 'E', road1)
                elif "WEST" in road1 and len(road1)>7:
                    road1 = re.sub(r'\bWEST\b', 'W', road1)
                elif "NORTH" in road1 and len(road1)>8:
                    road1 = re.sub(r'\bNORTH\b', 'N', road1)
                elif "SOUTH" in road1 and len(road1)>8:
                    road1 = re.sub(r'\bSOUTH\b', 'S', road1)
                route1 = re.sub(r'\s+','', road1)
                if "EAST" in road2 and len(road1)>7:
                    road2 = re.sub(r'\bEAST\b', 'E', road2)
                elif "WEST" in road2 and len(road1)>7:
                    road2 = re.sub(r'\bWEST\b', 'W', road2)
                elif "NORTH" in road2 and len(road1)>8:
                    road1 = re.sub(r'\bNORTH\b', 'N', road2)
                elif "SOUTH" in road2 and len(road1)>8:
                    road1 = re.sub(r'\bSOUTH\b', 'S', road2)
                route2 = re.sub(r'\s+','', road2)
                clean_road1 = route1.strip()
                clean_road2 = route2.strip()
                correction = difflib.get_close_matches(clean_road1, check, 1, 0.7)
                correction2 = difflib.get_close_matches(clean_road2, check, 1, 0.7)
                match1 = ''.join(correction)
                match2 = ''.join(correction2)
                if match1 == '' and match2 != '':
                    final_match = road1 + " & " + match2
                elif match1 != '' and match2 == '':
                    final_match = match1 + " & " + road2
                elif match1 == '' and match2 == '':
                    final_match = ""
                else:
                    final_match = match1 + " & " + match2
                add1 = re.sub(r'\s+', ' ',final_match)
                add2 = add1.strip()
            elif street_prep == " ":
                add2 = ""
            if add1[0:].isdigit() or add1 == "":
                srow.add_clean3 = ''
            else:
                arcpy.AddMessage("Probable match: "+add2)
                srow.add_clean3 = add2
        srows.updateRow(srow)
    del srow
    del srows

def city_cleaner(infiles):
    """Checks the given city field value and attempts to match it to existing Marion County cities, returns the original value otherwise."""
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        if srow.getValue(city) == None:
            srow.city_clean = ''
        else:
            town = srow.getValue(city)
            first = re.escape(town)
            second = first.upper()
            rep = re.sub(r'[^A-Z]+','',second)
            newer = rep.strip()
            known_cit = ["INDY", "INDPLS"]
            if newer in known_cit:
                newer = "INDIANAPOLIS"
            correct = difflib.get_close_matches(newer, cities, 1, 0.6)
            match = ''.join(correct)
            if match != '':
                srow.city_clean = match
                arcpy.AddMessage("Cleaned to: "+match)
            elif newer != '':
                srow.city_clean = newer
                arcpy.AddMessage("Retained: "+newer)
            else:
                srow.city_clean = ''
        srows.updateRow(srow)
    del srow
    del srows

def state_cleaner(infiles):
    """Checks the given state field value, cleans it of irregular characters and checks for Indiana specific references"""
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        if srow.getValue(state) == None:
            srow.state_clean = ''
        else:
            stater = srow.getValue(state)
            second = re.escape(stater)
            third = second.upper()
            rep = re.sub(r'[^A-Z]+','',third)
            newer = rep.strip()
            if newer == "INDIANA":
                newer = "IN"
            if newer != '':
                arcpy.AddMessage(newer)
                srow.state_clean = newer
            elif third != '':
                srow.state_clean = third
            else:
                srow.state_clean = ''
        srows.updateRow(srow)
    del srow
    del srows

def zip_cleaner(infiles):
    """Cleans the original zip code of irregular characters and returns a 5 digit zip ONLY"""
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        if srow.getValue(zip_code) == None:
            srow.zip_clean = ''
        else:
            zipper = srow.getValue(zip_code)
            zipper2 = str(zipper)
            third = re.escape(zipper2)
            rep2 = re.sub(r'[^0-9]+','',third)
            newer2 = rep2.strip()
            if newer2 != '':
                arcpy.AddMessage(newer2)
                srow.zip_clean = newer2[0:5]
            elif third != '':
                srow.zip_clean = third
            else:
                srow.zip_clean = ''
        srows.updateRow(srow)
    del srow
    del srows

def combo(infiles):
    """Creates a combination of the cleaned street and cleaned zip"""
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
    """Creates a final match field for comparison that examines the cleaned street with the cleaned zip to see if the a better match is created based on a zip to street
    dictionary"""
    pass1 = open(r'C:\Documents and Settings\aaburges\Desktop\ipass_docs\zip_dict.txt', 'rb')
    read1 = pass1.readline()
    splitter1 = read1.split(",")
    check = []
    for item in splitter1:
        matcher = ''.join(item)
        check.append(matcher)
    pass1.close()
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        if srow.getValue("street_cl") == ' ':
            srow.zip_street = ' '
        else:
            streeter = srow.getValue("st_combo")
            rep = re.sub(r'[^0-9A-Za-z&\s]+', '', streeter)
            newer = rep.strip()
            str_prep = newer.upper()
            fire = str_prep.split(' ')
            if str_prep == '' or str_prep == "":
                str_prep = " "
            if "&" in str_prep:
                cross1, cross2 = str_prep.split("&",1)
                str_prep = " "
                road1 = ''.join(cross1)
                road2 = ''.join(cross2)
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
            if street_prep != " ":
                street2 = re.sub(r'\s+','', street_prep)
                clean_str= street2.strip()
                correction = difflib.get_close_matches(clean_str, check, 1, 0.7)
                match1 = ''.join(correction)
                if match1 != '':
                    add1 = match1.strip()
                    add2 = add1[:-6]
                    final_match2 = str_num + " " + add2.strip()
                    final_match3 = re.sub(r'\s+', ' ', final_match2)
                else:
                    final_match3 = ''
            elif road1 != '' and road2 != '':
                if road2[-5:].isdigit:
                    road12 = road1 + " " + road2[-5:]
                else:
                    road12 = road1
                route1 = re.sub(r'\s+','', road12)
                route2 = re.sub(r'\s+','', road2)
                clean_road1 = route1.strip()
                clean_road2 = route2.strip()
                correction = difflib.get_close_matches(clean_road1, check, 1, 0.7)
                correction2 = difflib.get_close_matches(clean_road2, check, 1, 0.7)
                match12 = ''.join(correction)
                match2 = ''.join(correction2)
                if match12 == '' and match2 != '':
                    final_match = road1 + " & " + match2[:-6]
                elif match12 != '' and match2 == '':
                    final_match = match12[:-6] + " & " + road2
                elif match12 == '' and match2 == '':
                    final_match = ""
                else:
                    final_match = match12[:-6] + " & " + match2[:-6]
                final_match2 = final_match.strip()
                final_match3 = re.sub(r'\s+', ' ', final_match2)
            if final_match3 == '':
                srow.zip_street = ''
            else:
                arcpy.AddMessage("Narrowed match: "+final_match3)
                srow.zip_street = final_match3
        srows.updateRow(srow)
    del srow
    del srows
    
def add_select(infiles):
    """Takes the address match from each iteration of the matching process, compares all matches against the cleaned address
    and picks a final match"""
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
            arcpy.AddMessage("Final match: "+final2)
        else:
            f.write(streeter2+",")
            arcpy.AddMessage("Final match: "+streeter2)
            srow.fin_address = streeter2.upper()
        srows.updateRow(srow)
    del srow
    del srows
    f.close()

def finale(infiles):
    """Records address values that I-PASS was unable to match and formats so that
    I-PASS_Report.py can create a .csv of uniquely occurring values."""
    f = open('C:\\Documents and Settings\\aaburges\\Desktop\\ipass_docs\\unique.txt', 'rb')
    read2 = f.readline()
    diction = {}
    splitter = read2.split(",")
    for item in splitter:
        key,value = item.split(":")
        diction[key] = value
    f.close()
    srows = arcpy.UpdateCursor(infiles)
    for srow in srows:
        streets = srow.getValue("fin_address")
        if streets in diction:
            match = ''.join(diction[streets])
            srow.fin_address = match
            srows.updateRow(srow)
    del srow
    del srows


try:
    arcpy.SetProgressor("step", "Parsing initial data, setting up structure...", 0, 1, 1)
    setup(infile)
    arcpy.SetProgressorPosition(1)
    arcpy.ResetProgressor()
    arcpy.SetProgressor("step", "Matching addresses by frequent occurrences", 0, 2, 1)
    address_check(infile)
    arcpy.SetProgressorLabel("Checking address by moderate occurence...")
    arcpy.SetProgressorPosition(1)
    address_check2(infile)
    arcpy.SetProgressorLabel("Checking address by rare occurence...")
    arcpy.SetProgressorPosition(2)
    address_check3(infile)
    arcpy.ResetProgressor()
    arcpy.SetProgressor("step", "Cleaning city, state and zip...", 0, 3, 1)
    city_cleaner(infile)
    arcpy.SetProgressorPosition(1)
    state_cleaner(infile)
    arcpy.SetProgressorPosition(2)
    zip_cleaner(infile)
    arcpy.SetProgressorPosition(3)
    arcpy.ResetProgressor()
    arcpy.SetProgressor("step", "Asserting street to zip combinations", 0, 2, 1)
    combo(infile)
    arcpy.SetProgressorLabel("Checking address matches to given zip code...")
    arcpy.SetProgressorPosition(1)
    zip_to_street(infile)
    arcpy.SetProgressorPosition(2)
    arcpy.SetProgressor("step", "Calculating final matches and logging unmatched addresses...", 0, 2, 1)
    add_select(infile)
    arcpy.SetProgressorLabel("Cleaning up...")
    arcpy.SetProgressorPosition(1)
    finale(infile)
    arcpy.SetProgressorLabel("Fin!")
    arcpy.SetProgressorPosition(2)

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
    # delete temp fields
    arcpy.DeleteField_management(infile, "street_cl")
    arcpy.DeleteField_management(infile, "add_clean1")
    arcpy.DeleteField_management(infile, "add_clean2")
    arcpy.DeleteField_management(infile, "add_clean3")
    arcpy.DeleteField_management(infile, "zip_street")
    arcpy.DeleteField_management(infile, "st_combo")
    arcpy.ResetProgressor()
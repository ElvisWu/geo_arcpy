I-PASS Documentation
------------------------------------------------------------------------------------------
arcpy version (must have ArcGIS 10 installed!)

###########################################################################################
READ THIS FIRST!!!

You must download the following files for I-PASS to work:

IPASS_Advanced.py
IPASS_Report.py
ipass_check1.txt
ipass_check2.txt
ipass_check3.txt
unique.txt
zip_dict.txt
###########################################################################################

1. Set your IPASS text files
-------------------------------------------------------------------------------------------

Open IPASS_Advanced.py and find the comments marked "# Download the accompanying text files
 and set appropriate paths".


Change these paths to wherever you saved the given files above (you'll need to do this for 
all the .txt files) and save.
___________________________________________________________________________________________

2. Set your IPASS Report files
-------------------------------------------------------------------------------------------

Open IPASS_Report

Change the txt file paths to match the locations of your downloads. "result_log.csv" needs
to be set to an existing location on your computer.  This log will record all unique
addresses that I-PASS was unable to recognize or clean.

___________________________________________________________________________________________

3. Add to an ArcGIS toolbox
-------------------------------------------------------------------------------------------
(Subject to change once ArcGIS 10.1 is released)

Your first parameter needs to be set as a "table" as this will be your input table
(preferably a .csv or .dbf file.) and needs to be set as input.

The additional 4 parameters represent the following in order:

street address - set to input and "derived" from your table
city - same as above
state - same as above
zip_code - same as above

____________________________________________________________________________________________

4. Using I-PASS in ArcGIS
--------------------------------------------------------------------------------------------

I-PASS will add the following fields to your table:

fin_address -- The final cleaned address
city_clean -- The final cleaned city name
state_clean -- The final cleaned state abbreviation
zip_code -- The final zip code

I-PASS can take hours depending on the size of your table (5 hours on ~600,000 records.)

Known bugs:

I-PASS may fail if quotes exist in any field as well.  It is highly recommended that you clean
all quotes out of your address fields before running through I-PASS

I-PASS has failed when an address ended in \ as standard python escape has been known to fail
in ArcGIS.  I-PASS will not fail, however, simply because \ is in the address.
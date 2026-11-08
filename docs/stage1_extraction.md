Input:
- the input is the excel files from data/incoming, which we are filling
with the generate_data.py

Output:
- list of dictionaries... where dictionary is one row and the list is multiple rows
- each dict also has the file name, sheet name and row number

Steps:
- find the files in data/incoming/
- read the excel file and sheets inside
- separate the headers from the actual values (headers will be the keys, rows values)
- save it into dictionary
- to that dictionary - add the information about the sheet and file (source)
- save the whole dict with added info about source

What can go wrong with the files:
- the folder doesn't exist or is empty: there's nothing to read.
- a file that isn't Excel ends up in the folder
- empty blank rows in the middle of the data - would become dict full of None values
- renamed or misspelled column header (schema drift)

# csv_to_mcap.py

## Introduction

`csv_to_mcap.py` is a Python script that saves .csv to .mcap using the RTMaps runtime API.  

## How to Use

Place the folders of both rtmaps_csv.pck and rtmaps_mcap.pck in the local package folder.
Or update the code line 25 to point toward your package folder.
 
> `python csv_to_mcap.py CSV_INPUT_FOLDER MCAP_OUTPUT_FOLDER`

This will search for all csv in the input folder and save the mcap into the output folder 

### Verbose to print every RTMaps console output
 
> `python csv_to_mcap.py CSV_INPUT_FOLDER MCAP_OUTPUT_FOLDER --verbose`

This will print all RTMaps messages info, warnings, erros & parse
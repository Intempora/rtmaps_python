#!/usr/bin/env python3
# coding=utf-8
#
#  Copyright (C) INTEMPORA S.A.S
#  ALL RIGHTS RESERVED.
#

import argparse
import os 

import sys 
import time 

import datetime

rtmaps_api_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rtmaps")
sys.path.insert(0, rtmaps_api_path)
from rtmaps import RTMapsWrapper

# =======================================
# CONFIGURATION
# ======================================= 
root_folder = os.path.dirname(os.path.abspath(__file__))
diagram_path = os.path.join(root_folder, "diagrams", "csv_to_mcap.rtd") 
pck_path = os.path.join(root_folder, "packages")  

importer_name = "AdvancedCsvImporter_1"
exporter_name = "McapExporter_1"

VERBOSITY = False 

# =======================================
# Report function
# =======================================  
def onRtmapsReport(dummy, level: int, msg: bytes):
    """RTMaps message handle."""
    REPORT_INFO = 0
    REPORT_WARNING = 1
    REPORT_ERROR = 2
    REPORT_CMD = 3

    message = msg.decode("utf-8") 
    baselog = "[Runtime][{}]".format(datetime.datetime.now())
 
    # Only print Info & Parse if verbosity is True
    if VERBOSITY: 
        if level == REPORT_INFO:
            print(baselog + " : " + message) 
        if level == REPORT_CMD:
            print(baselog + " : " + message)
     
    # Always report warings & errors
    if level == REPORT_WARNING:
        print(baselog + " : " + message) 

    if level == REPORT_ERROR:
        print(baselog + " : " + message)

# =======================================
# Utils function
# =======================================  

def diagramIsRunning(maps):
    """Returns RTMaps diagram state."""
    return maps.get_current_time() != 0

def getAllFilesByExtension(ext):  
    files = []
    for file in os.listdir(csv_path): 
        if file.endswith(ext):
            # Prints only text file present in My Folder
            files.append(file)  

    print("Found [" + str(len(files)) + "] " + ext + " files") 
    return files

def createDiagram(maps):
    rtmaps.register_package("rtmaps_csv/rtmaps_csv.pck", pck_path)
    rtmaps.register_package("rtmaps_mcap.pck", pck_path + "/rtmaps_mcap") 
    rtmaps.parse("AdvancedCsvImporter " + importer_name)
    rtmaps.parse(importer_name + ".separator = <<Comma (,)>>")
    rtmaps.parse(importer_name + ".timestamp_unit = <<Seconds>>")
    #rtmaps.parse(importer_name + ".replay_mode = <<Immediate>>") 

    #AdvancedCsvImporter_1.separator = <<Semicolon (;)>>


def configureMCAPExporter(maps): 
    # Place components
    maps.parse("McapExporter " + exporter_name) 
    # Set MCAP output folder
    maps.parse(exporter_name + ".output_file_path = <<" + mcap_path + ">>")  
    # Set csv file
    maps.parse(importer_name + ".input_file = <<" + csv_path + "\\" + file + ">>")  
    
def connectImporterToExporter(maps):  
    # Get output names of csv importer
    importer_output_names = maps.get_output_names_for_component(importer_name)
    nb_importer_output = len(importer_output_names) - 1 # we don't want to save the eof to mcap 
    # Configure MCAP Exporter
    file_no_ext = os.path.splitext(file)[0]
    maps.parse(exporter_name + ".output_file_name = <<" + file_no_ext + ">>") 
    maps.parse(exporter_name + ".p_input_count = " + str(nb_importer_output))  

    # Set channel type to Floats
    # Connect CSV importer to MCAP exporter 
    for i in range(nb_importer_output): 
        maps.parse(exporter_name + ".inputs_" + str(i) + "_msg_type = <<Float(s)>>") 
        maps.parse(importer_output_names[i] + ".fifosize = " + str(1024)) 
        maps.parse(importer_output_names[i] + " -> " + exporter_name + ".topic_" + str(i))  
        
    # Auto set channels names based on csv outputs
    maps.parse(exporter_name + ".AutoTopicNames") 

    # Set every input in NeverSkipping
    exporter_input_names = maps.get_input_names_for_component(exporter_name)

    for topic in exporter_input_names: 
        maps.parse(topic + ".readerType = 1") 



# =======================================
# MAIN   
# ======================================= 
if __name__ == "__main__": 
    # Configure arguments
    argParser = argparse.ArgumentParser(
        description="".join((
            "%(prog)s\n",
            "\n"
            "Creates an RTMaps diagram to convert .csv to .mcap\n\n",
        )),
    )
    argParser.add_argument("csv_folder", type=str, help="Folder with .csv to process")
    argParser.add_argument("mcap_folder", type=str, help="Folder to save generated .mcap")
    argParser.add_argument("--verbose", action="store_true", help="prints rtmaps console in python console")
    args = argParser.parse_args(sys.argv[1:])

    # Read arguments 
    root_csv_folder = os.path.dirname(os.path.abspath(args.csv_folder))
    csv_path = os.path.join(root_folder, args.csv_folder ) 
    print("Input CSV Folder : " + csv_path) 

    root_mcap_folder = os.path.dirname(os.path.abspath(args.mcap_folder))
    mcap_path = os.path.join(root_folder, args.mcap_folder ) 
    print("Output MCAP Folder : " + mcap_path)  

    if args.verbose:
        VERBOSITY = True 
 
    # Fetch all csv files in Folder 
    csv_files = getAllFilesByExtension(".csv")  

    # =======================================
    # RTMAPS
    # =======================================  
    # Start an RTMaps Runtime engine instance, with console for logging
    rtmaps = RTMapsWrapper("--console") 

    # Assign RTMaps Report Reader Function
    rtmaps.register_report_reader(onRtmapsReport)

    # Create diagram  
    createDiagram(rtmaps) 

    # Try catch keyboard interrupt
    try:
        # Loop over all mf4 files in the recording folder
        for file in csv_files : 

            configureMCAPExporter(rtmaps) 
            connectImporterToExporter(rtmaps)
                
            # Run the configured diagram
            if not diagramIsRunning(rtmaps):
                print("\nWorking on : [" + file + "]")
                # Start post-processing
                rtmaps.run() 
                    
                end_ts = 0

                while diagramIsRunning(rtmaps): 
                    time.sleep(0.5)
                    eof = rtmaps.read_int64_timeout(importer_name + ".eof", 100)

                    if eof is not None :
                        end_ts = rtmaps.get_current_time()
                        rtmaps.shutdown() 
                        rtmaps.parse("kill " + exporter_name)
         
                print("Conversion to MCAP : [SUCCESS]")
                print("Duration : [" + str(end_ts) + "] us")

    except KeyboardInterrupt:
        print("Exit/Keyboard interrupt occurred") 
        if diagramIsRunning(rtmaps):
            rtmaps.shutdown()
 
    
    rtmaps.shutdown() 
    rtmaps = None
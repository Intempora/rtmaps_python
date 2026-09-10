import time
import datetime

from rtmaps import RTMapsWrapper 

VERBOSITY = True 

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


# Create RTMapsWrapper
rtm = RTMapsWrapper()

# Assign RTMaps Report Reader Function
rtm.register_report_reader(onRtmapsReport)

# Add components from standard_components package
rtm.add_component("Randint", "Randint_1")
rtm.add_component("SampleRate", "SampleRate_1")  
 
# Connect: Randint outputInteger -> DataViewer input_0
rtm.connect_components("Randint_1", "outputInteger", "SampleRate_1", "input")
 
# Set property on Randint
rtm.set_property("Randint_1", "vectorSize", 4)

# Randint will output data once per second
rtm.set_property("Randint_1", "period", 1000000)
rtm.set_property("Randint_1", "max", 100) 
  
# Run diagram
print("Starting diagram...")
try: 
    rtm.run() 
    
    # Run RTMaps for 10 seconds
    while rtm.get_current_time() <= 5000000 :   
        time.sleep(1) 
            
except KeyboardInterrupt:
    print("Exit/Keyboard interrupt occurred") 
finally :
    # Cleanup
    rtm.shutdown()
    print("RTMaps shutdown()")
 
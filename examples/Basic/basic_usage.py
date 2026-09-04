import time
from rtmaps import RTMapsWrapper 

# Create RTMapsWrapper
rtm = RTMapsWrapper()

# Add components from standard_components package
rtm.add_component("Randint", "Randint_1")
rtm.add_component("DataViewer", "DataViewer_1")  

# Connect: Randint outputInteger -> DataViewer input_0
rtm.connect_components("Randint_1", "outputInteger", "DataViewer_1", "input_0")
 
# Set property on Randint
rtm.set_property("Randint_1", "vectorSize", 4)

# Randint will output data once per second
rtm.set_property("Randint_1", "period", 1000000)
rtm.set_property("Randint_1", "max", 100) 

rtm.write_rtm_script("C:/Users/teolo/Documents/GitHub/rtmaps_python/examples/Basic/basic_usage.rtm")

# Configure multiple properties at once
# 
# properties = {
#     "vectorSize": 4,
#    "period": 1000000, 
#     "max": 100
# }
# 
# for prop, value in properties.items():
#     rtm.set_property("Randint_1", prop, value)


# Run diagram
print("Starting diagram...")
try: 
    rtm.run()

    # Run RTMaps for 10 seconds
    while rtm.get_current_time() <= 5000000 :  
        # Read output from Randint_1
        status = rtm.read_int32("Randint_1", "outputInteger", True)
        if status is not None:
            print(f"Randint_1 output: {status}")
        else:
            print("Randint_1 output: None (timeout or no data)")
             
        time.sleep(0.5)
            
    rtm.shutdown() 
            
except KeyboardInterrupt:
    print("Exit/Keyboard interrupt occurred") 
finally :
    # Cleanup
    rtm.shutdown()
    print("RTMaps shutdown()")

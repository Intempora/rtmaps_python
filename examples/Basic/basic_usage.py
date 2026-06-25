import time
from rtmaps import RTMapsAbstraction 

# Bypass singleton by creating instance directly
rtm = RTMapsAbstraction()

# Add components from standard_components package
rtm.add_component("Randint", "Randint_1")
rtm.add_component("DataViewer", "DataViewer_1") 

# Connect: Randint outputInteger -> DataViewer input_0
rtm.connect_components("Randint_1", "outputInteger", "DataViewer_1", "input_0")
 
# Set property on Randint
rtm.set_property("Randint_1", "vectorSize", 4)
rtm.set_property("Randint_1", "max", 100)

# Run diagram
print("Starting diagram...")
rtm.run()

# Read output from Randint_1
status = rtm.read_int32("Randint_1", "outputInteger", True)
if status is not None:
    print(f"Randint_1 output: {status}")
else:
    print("Randint_1 output: None (timeout or no data)")
 
# Cleanup
rtm.shutdown()
print("diagram stopped.")

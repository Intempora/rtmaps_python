import time
from rtmaps import RTMapsWrapper
 
# Create RTMaps instance (bypass singleton)
rtm = RTMapsWrapper()

# Build a data processing pipeline with multiple components
# Float_constants_generator -> Calc (Add) -> DataViewer

# Add components
rtm.add_component("Float_constants_generator", "FloatConstGen_1")
rtm.add_component("Calc", "Calc_Adder_1") 
rtm.add_component("DataViewer", "DataViewer_1")

# Configure Calc: perform addition operation. This creates the Calc inputs
rtm.set_property("Calc_Adder_1", "expression", "a + b")

# Connect components in a pipeline
# Float_constants_generator output -> Calc input_a
rtm.connect_components("FloatConstGen_1", "output", "Calc_Adder_1", "a")
# Float_constants_generator output -> Calc input_b (same signal for addition)
rtm.connect_components("FloatConstGen_1", "output", "Calc_Adder_1", "b")
# Calc output -> DataViewer_1 input
rtm.connect_components("Calc_Adder_1", "outputFloat", "DataViewer_1", "input_0") 

# Configure Float_constants_generator: generate two constant values
rtm.set_property("FloatConstGen_1", "value_1", 10.5)
rtm.set_property("FloatConstGen_1", "outputPeriod", 500000)  # 0.5 seconds 
 

print("Starting data processing pipeline...")
try:
    rtm.run()

    # Run for 8 seconds (4 reset periods)
    while rtm.get_current_time() <= 8000000:
        # Read accumulated value 
        status = rtm.read_float64_timeout("Calc_Adder_1", "outputFloat", True)
        if status is not None:
            print(f"Calc_Adder_1 output: {status}")
        else:
            print("Calc_Adder_1 output: None (timeout or no data)") 

        time.sleep(1)

    rtm.shutdown()

except KeyboardInterrupt:
    print("Keyboard interrupt occurred")
finally:
    rtm.shutdown()
    print("RTMaps shutdown complete")

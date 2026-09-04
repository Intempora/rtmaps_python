import time
from rtmaps import RTMapsWrapper

# Create wrapper and load existing diagram file
rtm = RTMapsWrapper()
diagram_file = "C:/Users/teolo/Documents/GitHub/rtmaps_python/examples/Basic/test_diagram.rtm"  # Change to your .rtm file path
print(f"Loading diagram from: {diagram_file}")

try:
    rtm.load_diagram(diagram_file)
    print("Diagram loaded successfully!")
    
    # Run the diagram
    print("\nStarting diagram...")
    rtm.run()
    
    # Monitor for 10 seconds (adjust time as needed)
    while rtm.get_current_time() <= 10000000:
        status = rtm.read_int32("DataViewer_1", "input_0", True)
        if status is not None:
            print(f"Time {rtm.get_current_time():.0f}: DataViewer input = {status}")
        else:
            print(f"Time {rtm.get_current_time():.0f}: No data yet")
        
        time.sleep(1)
    
    print("\nDiagram finished!")
    
except KeyboardInterrupt:
    print("Exit/Keyboard interrupt occurred")
finally:
    rtm.shutdown()
    print("RTMaps shutdown complete")

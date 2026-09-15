import time 
import multiprocessing
import psutil
import os 

from rtmaps import RTMapsWrapper 

import threading

def setCPUAffinity(component:str, targetedCore=0):
    # Add comps to fetch threadIDs  
    print("Adding monitoring components")
    p2o_name = "Prop2Output_" + component
    rtm.add_component("PropertyToOutput", p2o_name)
    rtm.set_property(p2o_name, "property_0_name", component + ".primaryThreadID") 
    
    # Get thread IDS 
    randint_id = rtm.read_int32(p2o_name, "output_0_primaryThreadID", True)
    print(component + " : Thread ID [" + str(randint_id) + "]")  
    
    #   Windows cannot set threads on specific core only full processes
    #   Linux apparently can do it
    try:
        native_id = threading.get_native_id() 
        pr = psutil.Process()
        print(str(pr))  

        # Pin specific thread to Core 0 (0-indexed)
        # Note: On Windows, use p.cpu_affinity() on the process level if targeting the main thread,
        # or use os-specific APIs, as psutil's per-thread affinity is primarily Linux-optimized.
        try:
            psutil.Process(pr.pid).cpu_affinity([targetedCore]) 
            print(f"Randint_1 Thread pinned to core " + str(targetedCore))
            
        except AttributeError:
            os.sched_setaffinity(native_id, {targetedCore})
            print(f"Randint_1 Thread pinned to core " + str(targetedCore))
        
    except Exception as e:
        print(e)


def CreateRTMapsDiagram(rtm:RTMapsWrapper):
    # Add components from standard_components package 
    print("Adding components")
    rtm.add_component("Randint", "Randint_1")
    rtm.add_component("DataViewer", "DataViewer_1")   

    # Set property on Randint
    print("Configuring components")
    rtm.set_property("Randint_1", "vectorSize", 4)

    # Randint will output data once per second
    rtm.set_property("Randint_1", "period", 1000000)
    rtm.set_property("Randint_1", "max", 100)  

    # Connect: Randint outputInteger -> DataViewer input_0
    print("Connecting components")
    rtm.connect_components("Randint_1", "outputInteger", "DataViewer_1", "input_0")

     
def RunRTMapsDiagram(rtm:RTMapsWrapper):
    # Run diagram 
    print("Starting diagram...\n")
    try: 

        # CPU affinity
        setCPUAffinity("Randint_1", targetedCore=0)
        setCPUAffinity("DataViewer_1", targetedCore=2)  
        
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
        print("\nRTMaps shutdown()")


if __name__ == "__main__":
    # Detect available cores
    cores = psutil.Process().cpu_affinity()
    print(f"System has {len(cores)} logical cores: {cores}")
 
    # Get the current thread's internal ID
    current = threading.current_thread()
    print(f"Thread Name: {current.name}")
    print(f"Thread Ident: {current.ident}")
    print(f"Thread Native ID: {current.native_id}")  # Python 3.8+

    # Create RTMapsWrapper
    rtm = RTMapsWrapper()
    CreateRTMapsDiagram(rtm)
    RunRTMapsDiagram(rtm)

import os
import threading
import time
from multiprocessing import Process

def worker_thread_logic(thread_core, thread_label):
    """
    Logic running inside the thread, explicitly pinning itself 
    to a sub-core after starting.
    """
    # 1. Get the actual Linux OS-level Thread ID (LWP)
    linux_tid = threading.get_native_id()
    
    # 2. Force-pin this specific thread to its designated core
    # First argument 'linux_tid' ensures ONLY this thread is pinned.
    os.sched_setaffinity(linux_tid, {thread_core})
    
    # 3. Verify the binding
    verified_cores = os.sched_getaffinity(linux_tid)
    print(f"    └─ [Thread-{thread_label}] OS-TID {linux_tid} explicitly pinned to Core {verified_cores}")
    
    # Simulate thread work loop
    for _ in range(3):
        time.sleep(1)


def isolated_process_entry(process_core, thread_cores_map):
    """
    Entry point for the spawned Process.
    """
    # 1. Pin the parent Process itself first
    current_pid = os.getpid()
    os.sched_setaffinity(0, {process_core})
    print(f"[Process] PID {current_pid} running. Main core restriction set to: {os.sched_getaffinity(0)}")
    
    # 2. Spawn internal threads and assign them their requested cores
    threads = []
    for label, target_thread_core in thread_cores_map.items():
        t = threading.Thread(
            target=worker_thread_logic, 
            args=(target_thread_core, label)
        )
        threads.append(t)
        t.start()
        
    # Wait for all threads inside this process to finish
    for t in threads:
        t.join()


if __name__ == '__main__':
    # EXAMPLE CONFIGURATION:
    # We want the Process overall to run on Core 2.
    # We want its internal Thread_A pinned explicitly to Core 3.
    # We want its internal Thread_B pinned explicitly to Core 4.
    MAIN_PROCESS_CORE = 2
    THREAD_CORES = {
        "A": 3,
        "B": 4
    }
    
    print(f"Root Script (PID {os.getpid()}) spawning isolated process layout...")
    
    # Launch the process
    p = Process(target=isolated_process_entry, args=(MAIN_PROCESS_CORE, THREAD_CORES))
    p.start()
    p.join()
    
    print("Execution complete.")
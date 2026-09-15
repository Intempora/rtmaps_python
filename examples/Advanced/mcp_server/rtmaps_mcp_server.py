import logging
import os 
import sys 
import glob
import re 
import subprocess
import time
 
from rtmaps import RTMapsWrapper  
from rtmaps_diagram import Diagram  
 
# # # # # # # # # # # # # # # # # # 
# # MCP SERVER
# # # # # # # # # # # # # # # # # #  
name = "rtmaps-mcp-server"
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(name) 
port = int(os.environ.get('USER_PORT', 8080))

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP(
    name,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
        # Add your specific gateway or domain here
        allowed_hosts=["localhost:*", "127.0.0.1:*", "host.docker.internal:*"],
        allowed_origins=["http://localhost:*", "http://host.docker.internal:*"],
    )
)
 

# # # # # # # # # # # # # # # # # # 
# # Utils
# # # # # # # # # # # # # # # # # #  
def find_file(directory: str, filename: str) -> str:
    for root, _, files in os.walk(directory):
        for file in files:
            if file == filename:
                return os.path.join(root, file)
    raise ValueError(f"{filename} not found in {directory}")

def basename_os_indep(path: str) -> str:
    elems = re.split("(/|\\\\)", path)
    if not elems:
        return ""
    return elems[-1]

def install_pck(pck) -> bool:
    if os.path.isfile(pck.get_path()):
        return False

    pck_file_name = basename_os_indep(pck.get_path())
    pck_name = pck_file_name.replace("rtmaps_", "").replace(".pck", "")
    os.makedirs(f"download_{pck_name}", exist_ok=True)
    os.chdir(f"download_{pck_name}")

    try:
        # Download the archive
        updater_get_args = ["rtmaps_updater", "get", f"pck_rtmaps_{pck_name}"]
        if pck.get_version():
            updater_get_args += ["-minversion", pck.get_version()]
            updater_get_args += ["-maxversion", pck.get_version()]
        logger.info("      - Executing [" + ", ".join(updater_get_args) + "]")
        subprocess.run(updater_get_args, stdout=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download package {pck_name} ({pck.get_version()}).")

    try:
        # Install package from archive
        zipfiles = glob.glob("*.zip")
        updater_install_args = ["rtmaps_updater", "install"] + zipfiles
        logger.info("      - Executing [" + ", ".join(updater_install_args) + "]")
        subprocess.run(updater_install_args, stdout=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install package {pck_name} ({pck.get_version()}).")
    os.chdir("..")
    return True

def diagramIsRunning(maps):
    """Returns RTMaps diagram state."""
    return maps.get_current_time() != 0

# # # # # # # # # # # # # # # # # # 
# # TOOLS
# # # # # # # # # # # # # # # # # #  
@mcp.tool()
def test_run(rtd_path: str, duration: str) -> str:
    """
    run a diagram for a limited time set by the duration argument
    
    Args:
        rtd_path: str: path to the diagram to load
        duration: str: duration of the run
        
    Returns:
        str: Response with status
    """

    logger.info("Tool called: test_run()")

    diag = rtmaps_diagram.Diagram()
    diag.read_file(rtd_path)

    comp_to_add = "Condition"
    diag.add_component(comp_to_add)
    cond = "<<Engine.time > " + duration + ">>"
    edit_component_property(rtd_path, comp_to_add, "Condition", cond)
    edit_component_property(rtd_path, comp_to_add, "then", "shutdown") 


@mcp.tool()
def edit_component_property(rtd_path: str, comp: str, prop: str, newvalue: str) -> str: 
    """
    edit a property of one component on the diagram at rtd_path
    
    Args:
        rtd_path: str: path to the diagram to load
        comp:     str: name of the component instance to edit
        prop:     str: component's property to edit
        newvalue: str: new value to put in the property
        
    Returns:
        str: Response with status
    """

    logger.info("Tool called: edit_component_property()")

    diag = rtmaps_diagram.Diagram() 
    edited_rtd_path = rtd_path[:-4] + "_edited.rtd"

    try:
        diag.read_file(rtd_path)
    except:
        logger.error(f"Could not open diagram {rtd_path}")
        return f"Could not open diagram {rtd_path}"

    comp_to_edit = diag.get_components(comp)  

    if len(comp_to_edit) == 0: 
        logger.error(f"No component {comp} found in diagram {rtd_path}")
        return f"No component {comp} found in diagram {rtd_path}"


    for c in comp_to_edit:
        try:
            c.set_property(prop, newvalue) 
            logger.info(f"Success !")

        except Exception as e: 
            logger.error(f"{str(e)} Could not set {prop} for component {comp.get_name()}")
            return f"Could not set {prop} for component {comp.get_name()}"
        
    diag.write_file(edited_rtd_path)    
    return "Component edit component's property and saved the diagram as " + edited_rtd_path     


@mcp.tool()
def run_replay_diagram(rtd_path: str) -> str:  
    """
    Replay diagram with a player until there is no more data to replay
    
    Args:
        rtd_path: str: path to the diagram to load
        
    Returns:
        str: Response with status
    """

    logger.info("Tool called: run_replay_diagram()")

    diag = rtmaps_diagram.Diagram()
    diag.read_file(rtd_path)

    # Check if diagram has at least 1 player
    players = diag.get_components("Player") 

    if len(players) == 0:
        logger.error(f"No player found in diagram {rtd_path}")
        return "No player found in diagram. Nothing to replay"

    rtmaps = RTMapsWrapper("--console") 
    logger.info("Loading selected diagram " + rtd_path) 
    rtmaps.parse("loaddiagram <<" + rtd_path + ">>") 
 
    # Run the configured diagram
    if not diagramIsRunning(rtmaps):
        print("\nRunning diagram for " + rtd_path)
        # Start post-processing
        rtmaps.run() 

    start = time.time() 

    # Periodically test progress, report about it, then shutdown.
    player_percentage = rtmaps.get_integer_property("Player_1.percentage")
    last_reported_percentage = 0
    last_report_time = time.time()
    while player_percentage < 100:
        if (player_percentage - last_reported_percentage >= 10) or (time.time() - last_report_time > 1):
            logger.info("RTMaps progress... {}%".format(player_percentage))
            last_reported_percentage = player_percentage
            last_report_time = time.time()
        time.sleep(0.1)
        player_percentage = rtmaps.get_integer_property("Player_1.percentage")
  
    rtmaps.shutdown()


    end = time.time()
    process_time = end - start 

    logger.info("Replay Done for " + rtd_path + " in " + str(process_time) + " secondes")  
    return "Diagram successfully ran for " + str(process_time) + " seconds"


@mcp.tool() 
def install_required_pck(rtd_path: str) -> str:  
    """
    list required packages by the diagram and install missing ones
    
    Args:
        rtd_path: str: path to the diagram to load
        
    Returns:
        str: Response with status
    """

    logger.info("Tool called: install_required_pck()")
 
    diag = rtmaps_diagram.Diagram()
    diag.read_file(rtd_path)

    required_packages = diag.get_required_packages()
    if required_packages:
        logger.info(f"Required packages:")
        for pck in required_packages:
            version_str = pck.get_version() if pck.get_version() else "no version specified"
            logger.info(f"  - {pck.get_path()} ({version_str})")
            logger.info(f"      - Fetching...", end="\r")
            did_install = install_pck(pck)
            if did_install:
                logger.info(f"      - Installed version {pck.get_version()}")
                pck_filename = basename_os_indep(pck.get_path())
                path = find_file("/opt/rtmaps/packages", pck_filename)
                pck.set_path(path)
                logger.info(f"      - Set package path to {pck.get_path()}")
            else:
                logger.info(f"      - Was already installed")
    else :
        return "All required packages were already installed"
    return "All required packages installed successfully !"


@mcp.tool()
def set_diagram_afap(rtd_path: str) -> str: 
    """
    Configure all components on a diagram to make it run as fast as possible (AFAP mode)
    
    Args:
        rtd_path: str: path to the diagram to load
        
    Returns:
        str: Response with status
    """ 

    logger.info("Tool called: set_diagram_afap()")
 
    diag = rtmaps_diagram.Diagram()

    try :
        diag.read_file(rtd_path)
    except:
        return "Could not load file " + rtd_path
    
    # Check if diagram has at least 1 player
    players = diag.get_components("Player") 

    if len(players) == 0:
        logger.error(f"No player found in diagram {rtd_path}")
        return "No player found in diagram " + rtd_path

    TIME_LAG_INFINITE = -1
    READER_TYPE_NEVER_SKIPPING = 1
 
    logger.info(f"Configuring {rtd_path} for AFAP mode..")

    try :

        # Set all players' time lag to infinite
        for player in diag.get_components("Player"):
            player.set_property("timelag", TIME_LAG_INFINITE, rtmaps_diagram.RTMAPS_TYPE_INT)
            logger.info(f"  - Set {player.get_name()}.timelag to infinite")

        # Set all players' outputs' replay mode to immediate
        for player in diag.get_components("Player"):
            for output in player.get_outputs():
                output.set_property("replayMode", "3|1|Normal|Immediate|Timestamp", rtmaps_diagram.RTMAPS_TYPE_ENUM)
                logger.info(f"  - Set {player.get_name()}.{output.get_name()}.replayMode to Immediate")

        # Reduce all players' outputs' fifoSize to save RAM (and prevent OOME crashes)
        max_fifo_size = int(os.environ["MAX_FIFO_SIZE"]) if "MAX_FIFO_SIZE" in os.environ else 2
        for player in diag.get_components("Player"):
            for output in player.get_outputs():
                output.set_property("fifosize", max_fifo_size)
                logger.info(f"  - Set {player.get_name()}.{output.get_name()}.fifoSize to {max_fifo_size}")

        # Set all inputs to NeverSkippingRecord
        for comp in diag.get_components():
            for inp in comp.get_inputs():
                inp.set_property("readerType", READER_TYPE_NEVER_SKIPPING, rtmaps_diagram.RTMAPS_TYPE_INT)
                logger.info(f"  - Set {comp.get_name()}.{inp.get_name()}.readerType to NeverSkippingRecord")
    
        edited_rtd_path = rtd_path[:-4] + "_afap.rtd"
        diag.write_file(edited_rtd_path)

        logger.info(f"Success !")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return "Error while configuring diagram !"
    finally:
        return "Diagram successfully set to run as fast as possible and saved as " + edited_rtd_path
 

# # # # # # # # # # # # # # # # # # 
# # MAIN
# # # # # # # # # # # # # # # # # #  
if __name__ == "__main__":
    """
    Initialize and start an RTMAPS MCP server.

    Available tools :
        run_replay_diagram(rtd_path: str) -> str    
            starts an rtmaps instance to run the diagram at rtd_path
    
        install_required_pck(rtd_path: str) -> str
            install all the packages required by the diagram at rtd_path

        set_diagram_afap(rtd_path: str) -> str
            configure the diagram at rtd_path to run as fast as possible

        edit_component_property(rtd_path: str, comp: str, prop: str, newvalue: str) -> str: 
            edit one property of one component

    """
    logger.info(f"Starting MCP Server on port {port}...")
    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Server terminated")
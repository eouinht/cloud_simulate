import threading
# simulation/state.py
# Save global state 
hosts = {}      # {hostname: Host object}
vms = {}        # {uuid: VM object}
                # timestamp = {}
list_vms = []   # Danh sách uuid của tất cả VM
timestamp = {"current": 0}

step_event = threading.Event()

# simulation sets step_ready_event to notify scheduler a new step is ready
step_ready_event = threading.Event()
# scheduler sets step_continue_event to allow simulation to continue
step_continue_event = threading.Event()
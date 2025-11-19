from .vm import VM
from .libs import Logger
# simulation/state.py
# Save global state 
hosts = {}   # {hostname: Host object}
vms = {}     # {uuid: VM object}
# timestamp = {}

timestamp = {"current": 0}
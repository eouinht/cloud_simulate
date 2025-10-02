from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from simpy import Environment
import pandas as pd
from simulation.env import create_simulation_env
from simulation.libs import Logger

# ===========================================
# CONFIGURATION
# ===========================================
DATA_FILE = "/home/thuong/data/sim_thuong/data/test_simulate.csv"  # You can change this to your dataset path

# ===========================================
# INITIALIZATION
# ===========================================
app = FastAPI(title="Cloud Simulation API", version="1.0.0")

# Allow remote control from other computers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict to known IPs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset
df = pd.read_csv(DATA_FILE)
simpy_env = Environment()
run_one_step, hosts = create_simulation_env(simpy_env, df)


# ===========================================
# HELPER FUNCTIONS
# ===========================================
def serialize_host(host):
    """Convert Host object to JSON serializable dict."""
    return {
        "hostname": host.hostname,
        "cpu_usage": host.host_cpu_usage,
        "num_vms": len(host.vms),
    }

def serialize_vm(vm):
    """Convert VM object to JSON serializable dict."""
    return {
        "uuid": vm.uuid,
        "cpu_usage": vm.cpu_usage,
        "cpu_allocated": vm.cpu_allocated,
        "cpu_steal": vm.vm_cpu_steal,
        "net_in": vm.vm_network_in,
        "net_out": vm.vm_network_out,
        "migrated": getattr(vm, "migrated", False),
    }

# ===========================================
# ROUTES
# ===========================================
@app.get("/")
def root():
    return {"message": "Cloud Simulation API is running."}

@app.post("/step")
def step():
    """Advance the simulation by one step."""
    run_one_step()
    return {"message": "Simulation advanced by 1 step."}

@app.get("/hosts")
def get_hosts():
    """Return summary of all hosts."""
    return {hn: serialize_host(host) for hn, host in hosts.items()}

@app.get("/vms")
def get_vms():
    """Return all VMs across all hosts."""
    all_vms = []
    for hn, host in hosts.items():
        for vm in host.vms:
            vm_info = serialize_vm(vm)
            vm_info["host"] = hn
            all_vms.append(vm_info)
    return all_vms

@app.post("/migrate")
def migrate_vm(uuid: str, target_host: str):
    """Migrate VM from its current host to a target host."""
    # Find VM
    src_host = None
    vm_obj = None
    for host in hosts.values():
        if uuid in host.uuid_to_vm:
            src_host = host
            vm_obj = host.uuid_to_vm[uuid]
            break

    if vm_obj is None:
        raise HTTPException(status_code=404, detail="VM not found.")

    if target_host not in hosts:
        raise HTTPException(status_code=400, detail="Target host not found.")

    if src_host.hostname == target_host:
        raise HTTPException(status_code=400, detail="Target host is the same as source.")

    # Perform migration
    Logger.info(f"Migrating VM {uuid} from {src_host.hostname} to {target_host}")
    src_host.remove_vm(uuid)
    hosts[target_host].add_vm(
        uuid,
        vm_obj.cpu_usage,
        vm_obj.vm_cpu_steal,
        vm_obj.cpu_allocated,
        vm_obj.vm_network_in,
        vm_obj.vm_network_out,
    )

    # Mark VM as migrated
    hosts[target_host].uuid_to_vm[uuid].migrated = True
    return {"message": f"VM {uuid} migrated to {target_host}"}

@app.post("/reset")
def reset():
    """Reset the entire simulation back to step 0."""
    global simpy_env, run_one_step, hosts
    simpy_env = Environment()
    run_one_step, hosts = create_simulation_env(simpy_env, df)
    return {"message": "Simulation has been reset to step 0."}

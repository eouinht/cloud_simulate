from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from simulation.libs import Logger
# from simulation.env import 
from simulation import state
from simulation.vm import VM

app = FastAPI(
    title="Cloud Simulation API",
    description="Control simulation via API",
    version="1.0.0"
)



@app.get("/")
def root():
    return {"message": "Welcome to the Cloud Simulation API! Visit /docs for interactive API docs."}

# @app.post("/step")
# def step_simulation():
#     result = state.simulate_one_step()
#     return result
# List all hosts
@app.get("/hosts")
def list_hosts():
    response = {
        "timestamp": state.timestamp if hasattr(state, "timestamp") else None,
        "hosts": []
    }
    for hn, h in state.hosts.items():
        response["hosts"].append({
            "hostname": hn,
            # "cpu_usage": h.cpu_usage,
            "total_memory": h.total_memory,
            "mem_in_used": h.mem_in_used,
            "num_vms": len(h.uuid_to_vm)
        })
    return response
#List VMs on a specific host
@app.get("/hosts/{hostname}")
def get_host(hostname: str):
    hostname_list = list(state.hosts.keys())
    print(f"Hostname_list: {hostname_list} ")
    try:
        hostname = int(hostname)
    except ValueError:
        # Nếu không ép được thì giữ nguyên (tránh crash)
        pass

    if hostname not in hostname_list:
        return {"error": f"Host {hostname} not found"}
    host = state.hosts[hostname]
    vm_list = []
    for vm_uuid, vm in host.uuid_to_vm.items():
        vm_list.append({
                "uuid": vm_uuid,
                "cpu_usage": vm.cpu_usage,
                "vm_cpu_steal": vm.vm_cpu_steal,
                "cpu_allocated": vm.cpu_allocated,
                "memory":vm.memory,
                "network_in": vm.net_in,
                "network_out": vm.net_out,
                "migrated" : vm.migrated,
                "placemented" : vm.placemented,
        })
    return {
        "hostname" : hostname,
        "cpu_usage": host.cpu_usage,
        "num_vms": len(host.uuid_to_vm),     
        "vms": vm_list,  
    }
    
class CreateVMRequest(BaseModel):
    uuid: str | None = None
    cpu_allocated: float = 1.0
    cpu_usage: float = 0.0
    vm_cpu_steal: float = 0.0
    net_in: float = 0.0
    net_out: float = 0.0
    
class AssignVMRequest(BaseModel):
    uuid: str

@app.post("/creat_vm")
def creat_vm(req: CreateVMRequest):
    if req.uuid in state.vms:
        return {"error": f"VM {req.uuid} already exists"}
    vm = VM(
        
        uuid = req.uuid,
        cpu_allocated = req.cpu_allocated,
        cpu_usage = req.cpu_usage,
        vm_cpu_steal= req.vm_cpu_steal,
        net_in = req.net_in,
        net_out = req.net_out,
        
    )
    
    state.vms[vm.uuid] = vm
    
    return {
        "status" : "create new vm is successfully",
        "vm": {
            "uuid": vm.uuid,
            "cpu_allocated": vm.cpu_allocated,
            "cpu_usage": vm.cpu_usage,
            "net_in": vm.net_in,
            "net_out": vm.net_out,
            "host": vm.hostname, #Chua gan host
        }
    }
    
@app.post("/hosts/{hostname}/assign-vm")
def assign_vm(hostname: str, req: AssignVMRequest):
    
    hostname = int(hostname)
    
    if hostname not in state.hosts:
        return {"error": f"Host {hostname} is not exist"}
    if req.uuid not in state.vms:
        return {"error": f"Vm {req.uuid} is not exist"}
    host = state.hosts[hostname]
    vm = state.vms[req.uuid]
    # Tag vm to host
    host.uuid_to_vm[vm.uuid] = vm
    vm.assign_host(host)
    return {
        "status": f"successfully embeded {vm.uuid} to host {hostname}",
        "host": hostname,
        "vm": vm.uuid
    }

class MigrateVMRequest(BaseModel):
    uuid: str
    des_host: str
@app.post("/migrate")
def migrate_vm_api(req: MigrateVMRequest):
    
    uuid = req.uuid
    target_host = req.des_host
    target_host = int(target_host)
    
    # Validate VM existence
    if uuid not in state.vms:
        raise HTTPException(status_code=404, detail=f"VM {uuid} not found in system.")

    # Validate target host
    if target_host not in state.hosts:
        raise HTTPException(status_code=404, detail=f"Host {target_host} not found in system.")

    vm = state.vms[uuid]
    
    # Get current host
    cur_hostname = vm.hostname
    
    if cur_hostname is None:
        raise HTTPException(status_code=500, detail=f"VM {uuid} is not assign to any host.")

    if cur_hostname == target_host:
        raise HTTPException(status_code=400, detail="VM is already on the target host.")

    cur_host = state.hosts[cur_hostname]
    tar_host = state.hosts[target_host]

    # Get VM object
    if uuid not in cur_host.uuid_to_vm:
        raise HTTPException(status_code=500, detail=f"VM {uuid} missing from host {cur_hostname} state.")
    vm = cur_host.uuid_to_vm.pop(uuid)
    if vm in cur_host.vms:
        cur_host.vms.remove(vm)

    # Assign VM to new host
    tar_host.vms.append(vm)
    tar_host.uuid_to_vm[vm.uuid] = vm
    vm.migrated_vm(tar_host)

    # Update both hosts
    cur_host.update_after_change()
    tar_host.update_after_change()

    # Log and return result
    Logger.succeed(f"VM {uuid} migrated from {cur_hostname} → {target_host}")

    return {
        "message": f"VM {uuid} migrated from {cur_hostname} → {target_host}",
        "from": cur_hostname,
        "to": target_host,
        "timestamp": state.timestamp,
        "vm": {
            "uuid": uuid,
            "host": target_host,
            "cpu_usage": vm.cpu_usage,
            "vm_cpu_steal": vm.vm_cpu_steal,
            "cpu_allocated": vm.cpu_allocated,
            "network_in": vm.net_in,
            "network_out": vm.net_out
        }
    }
@app.get("/vm/{uuid}/steal_time")
def get_vm_steal_time(uuid: str):
    """
    Return the current steal time (%) of a VM.
    """

    # --- Kiểm tra VM tồn tại ---
    vm = state.vms[uuid]
    if vm is None:
        raise HTTPException(status_code=404, detail=f"VM {uuid} not found in system.")

    # --- Lấy hostname hiện tại ---
    hostname = vm.get("host")
    if hostname is None or hostname not in state.hosts:
        raise HTTPException(status_code=404, detail=f"Host not found for VM {uuid}.")

    host = state.hosts[hostname]

    # --- Kiểm tra VM có thực sự thuộc host này không ---
    host_vm = host.uuid_to_vm.get(uuid)
    if host_vm is None:
        raise HTTPException(status_code=404, detail=f"VM {uuid} not found in host {hostname} state.")

    # --- Tính toán steal time ---
    if not hasattr(host_vm, "compute_steal_time"):
        raise HTTPException(status_code=500, detail="VM class missing compute_steal_time() method.")

    steal_time = host_vm.compute_steal_time()
    # --- Trả kết quả ---
    return {
        "timestamp": state.timestamp,
        "uuid": uuid,
        "host": hostname,
        "steal_time": steal_time,
    }

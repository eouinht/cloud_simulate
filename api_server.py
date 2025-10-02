from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from simulation.libs import Logger
# from simulation.env import 
from simulation import state


app = FastAPI(
    title="Cloud Simulation API",
    description="Control simulation via API",
    version="1.0.0"
)

# # Sample in-memory hosts & VMs
# hosts = {
#     "host1": {"vms": ["vm11", "vm12"]},
#     "host2": {"vms": ["vm21", "vm22"]},
# }

@app.get("/")
def root():
    return {"message": "Welcome to the Cloud Simulation API! Visit /docs for interactive API docs."}

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
            "cpu_usage": h.host_cpu_usage,
            "num_vms": len(h.uuid_to_vm)
        })
    return response
#List VMs on a specific host
@app.get("/hosts/{hostname}")
def get_host(hostname: str):
    if hostname not in state.hosts:
        return {"error": f"Host {hostname} not found"}
    host = state.hosts[hostname]
    vm_list = []
    for vm_uuid, vm in host.uuid_to_vm.items():
        vm_list.append({
                "uuid": vm_uuid,
                "cpu_usage": vm.cpu_usage,
                "cpu_allocated": vm.cpu_allocated,
                "network_in": vm.net_in,
                "network_out": vm.net_out,
                "migrated" : vm.migrated,
                "placemented" : vm.placemented,
        })
    return {
        "hostname" : hostname,
        "cpu_usage": host.host_cpu_usage,
        "vms": vm_list,
        "num_vms": len(host.uuid_to_vm),
       
    }
@app.get("/status")
def get_status():
    """Return the current status of all hosts and their Vms"""
    status = {}
    
    # Review all host
    for hostname, host in host.items():
        # Take host info
        host_info = {
            "host_cpu_usage": host.host_cpu_usage,
            "vms": []
        }
        
        # Take list Vm in host
        for uuid, vm in host.uuid_to_vm.items():
            vm_info = {
                "uuid": uuid,
                "cpu_usage": vm.cpu_usage,
                "cpu_steal": vm.cpu_steal,
                "cpu_allocated": vm.cpu_allocated,
                "net_in": vm.net_in,
                "net_out": vm.net_out,
                "migrated": vm.migrated, 
                "placement": vm.placemented,
            }
            host_info["vms"].append(vm_info)
        status[hostname] = host_info
    return status 

# # Request body fo creat new VM
# class CreatVMRequest(BaseModel):
#     vm_name: str
#     target_host: str
# @app.post("/creat_vm")
# def creat_vm(req: CreatVMRequest):
#     # Check target_host  is instant
#     if req.target_host not in hosts:
#         raise HTTPException(status_code=404, detail=f"Target host {req.target_host} not found")
#     # Check name VM is already exits
#     for h, data in hosts.items():
#         if req.vm_name in data["vms"]:
#             raise HTTPException(status_code=400, detail=f"VM {req.vm_name} already exists on host {h}")
#     # Actually create VM (assuming Host has a method like add_vm)
#     vm = hosts[req.target_host].add_vm(req.vm_name)
#     vm.placemented = True
    
#     return {
#         "status": "success",
#         "vm": req.vm_name,
#         "host": req.target_host,
#         "message": f"VM {req.vm_name} created on host {req.target_host}"
# }
    
    
# # Request body model for VM migration
# class MigrateRequest(BaseModel):
#     vm_name: str
#     target_host: str
    
# # Migrate a VM from one host to another
# @app.post("/migrate")
# def migrate_vm_api(req: MigrateRequest):
#     src_host = None
#     src_vm = None
    
#     # Find the source host containing the VM
#     src_host = None
#     for h, host in hosts.items():
#         if req.vm_name in host.uuid_to_vm:
#             src_host = h
#             src_vm = host.uuid_to_vm[req.vm_name]
#             break

#     if src_host is None:
#         raise HTTPException(status_code=404, detail=f"VM {req.vm_name} not found")
#     if req.target_host not in hosts:
#         raise HTTPException(status_code=404, detail=f"Target host {req.target_host} not found")
    
#     # Remove from source and add to target
#     hosts[src_host].remove(req.vm_name)
#     hosts[req.target_host].add_vm(req.vm_name)
#     # Update flags
#     src_vm.migrated = True
#     src_vm.placement = True

#     return {
#         "status": "success",
#         "src_host": src_host,
#         "dst_host": req.target_host,
#         "vm": req.vm_name
#     }


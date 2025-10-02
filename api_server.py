from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Cloud Simulation API",
    description="Control simulation via API",
    version="1.0.0"
)

# Sample in-memory hosts & VMs
hosts = {
    "host1": {"vms": ["vm11", "vm12"]},
    "host2": {"vms": ["vm21", "vm22"]},
}

@app.get("/")
def root():
    return {"message": "Welcome to the Cloud Simulation API! Visit /docs for interactive API docs."}

# List all hosts
@app.get("/hosts")
def list_hosts():
    return {"hosts": list(hosts.keys())}

# List VMs on a specific host
@app.get("/hosts/{hostname}/vms")
def list_vms(hostname: str):
    if hostname not in hosts:
        return {"error": "Host not found"}
    return {"vms": hosts[hostname]["vms"]}

# Request body model for VM migration
class MigrateRequest(BaseModel):
    vm_name: str
    target_host: str

# Migrate a VM from one host to another
@app.post("/migrate")
def migrate_vm_api(req: MigrateRequest):
    # Find the source host containing the VM
    src_host = None
    for h, data in hosts.items():
        if req.vm_name in data["vms"]:
            src_host = h
            break

    if src_host is None:
        return {"error": f"VM {req.vm_name} not found"}
    if req.target_host not in hosts:
        return {"error": f"Target host {req.target_host} not found"}

    # Move the VM
    hosts[src_host]["vms"].remove(req.vm_name)
    hosts[req.target_host]["vms"].append(req.vm_name)

    return {"status": "success", "src_host": src_host, "dst_host": req.target_host}


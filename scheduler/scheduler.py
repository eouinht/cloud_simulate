import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import requests
from simulation.libs import Logger
import requests


API = "http://127.0.0.1:8000"

CPU_OVERLOAD = 80
CPU_UNDERLOAD = 50
MAX_STEP = 300

def get_current_step(timeout=5):
    start = time.time()
    while True:
        try:
            r = requests.get(f"{API}/timestamp")
            if r.status_code == 200:
                return r.json().get("current", 0)
        except Exception as e:
            Logger.warning(f"Cannot fetch timestamp: {e}")
        if time.time() - start > timeout:
            Logger.warning("Timeout getting timestamp, returning 0")
            return 0
        time.sleep(0.01)

def get_host_detail(hostname):
    try:
        r = requests.get(f"{API}/hosts/{hostname}")
        if r.status_code == 200:
            return r.json()
        Logger.warning(f"Cannot get host {hostname}: {r.text}")
    except Exception as e:
        Logger.error(f"Exception getting host {hostname}: {e}")
    return None

def migrate_vm(vm_uuid, target_host):
    try:
        payload = {"uuid": vm_uuid, "des_host": str(target_host)}
        r = requests.post(f"{API}/migrate", json=payload)
        if r.status_code == 200:
            Logger.succeed(f"Migrated VM {vm_uuid} -> Host {target_host}")
        else:
            Logger.warning(f"Migration failed: {r.json()}")
    except Exception as e:
        Logger.error(f"Error calling migrate API: {e}")

def simple_scheduler(max_steps=MAX_STEP):
    last_step = 0
    Logger.info("============== Starting Simple Scheduler ===============")
    
    for _ in range(max_steps):
        step = get_current_step()
        if step <= last_step:
            step = last_step
        last_step = step
        Logger.info(f"Scheduler Step {step}:")
        
        try:
            hosts_data = requests.get(f"{API}/hosts").json()["hosts"]
        except Exception as e:
            Logger.error(f"Failed to get hosts info: {e}")
            continue

        overloaded, underloaded = [], []

        # Xử lý host dựa trên CPU usage từ API
        for h in hosts_data:
            hostname = h["hostname"]
            cpu = h.get("cpu_usage", 0.0)  # lấy CPU từ API
            num_vms = h.get("num_vms", 0)

            Logger.info(f"[DEBUG] Host {hostname} current CPU usage: {cpu:.2f}% | VMs: {num_vms}")

            if cpu > CPU_OVERLOAD and num_vms > 0:
                overloaded.append((hostname, cpu))
            elif cpu < CPU_UNDERLOAD:
                underloaded.append((hostname, cpu))

        if not overloaded or not underloaded:
            Logger.info("No migration needed this step.")
        else:
            # chọn host ít tải nhất làm target
            target_host = min(underloaded, key=lambda x: x[1])[0]
            for src_host, _ in overloaded:
                # lấy chi tiết host từ API
                detail = get_host_detail(src_host)
                if not detail or not detail.get("vms"):
                    continue
                
                # chọn VM CPU cao nhất (dựa trên CPU usage từ API)
                vm_to_migrate = max(detail["vms"], key=lambda v: v["cpu_usage"])
                migrate_vm(vm_to_migrate["uuid"], target_host)

        Logger.info(f"Step {step} done.\n")

    Logger.info("Scheduler finished all steps.")

if __name__ == "__main__":
    simple_scheduler(MAX_STEP)

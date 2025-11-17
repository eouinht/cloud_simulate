import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import requests
from simulation.libs import Logger
from simulation import state

API = "http://127.0.0.1:8000"

CPU_OVERLOAD = 80
CPU_UNDERLOAD = 50
MAX_STEP = 300 # 300 timestamps provided for each VM in the trace.

def get_host_detail(hostname):
    """Lấy chi tiết host từ API"""
    try:
        r = requests.get(f"{API}/hosts/{hostname}")
        if r.status_code == 200:
            return r.json()
        else:
            Logger.warning(f"Cannot get host {hostname} detail: {r.text}")
            return None
    except Exception as e:
        Logger.error(f"Exception getting host {hostname} detail: {e}")
    return None

def migrate_vm(vm_uuid, target_host):
    """Gọi API migrate VM"""
    try:
        payload = {"uuid": vm_uuid, "des_host": str(target_host)}
        r = requests.post(f"{API}/migrate", json=payload)
        if r.status_code == 200:
            Logger.succeed(f"Migrated VM {vm_uuid} to host {target_host}")
        else:
            Logger.warning(f"Migration failed: {r.json()}")
    except Exception as e:
        Logger.error(f"Error calling migrate API: {e}")
        
def syn_time(last_step):
    while True:
        try:
            current_step = state.timestamp.get("current", 0)
            if current_step > last_step:
                return current_step
        except:
            pass
        
        
def simple_schedular(max_steps=MAX_STEP):
    last_step = 0
    Logger.info("============== Starting Simple Scheduler ===============")
    for _ in range(max_steps):
        
        overloaded, underloaded = [], []
        step = syn_time(last_step)
        last_step = step
        Logger.info(f"Scheduler Step {step}:")
        try:
            hosts_data = requests.get(f"{API}/hosts").json()["hosts"]
        except Exception as e:
            Logger.error(f"Failed to get hosts info: {e}")
            continue
        for h in hosts_data:
            hostname = h["hostname"]
            detail = get_host_detail(hostname)
            if not detail:
                continue
            
            cpu = detail["cpu_usage"]
            Logger.info(f"[DEBUG] Host {hostname} current CPU usage: {cpu:.2f}%")
            if cpu > CPU_OVERLOAD and detail["num_vms"] > 0:
                overloaded.append((hostname, cpu))
            if cpu < CPU_UNDERLOAD:
                underloaded.append((hostname, cpu))
        if not overloaded or not underloaded:
            Logger.info("No migration needed this step.")
        else:
            # chọn host ít tải nhất làm target
            target_host = min(underloaded, key=lambda x: x[1])[0]
            for src_host, _ in overloaded:
                detail = get_host_detail(src_host)
                if not detail.get("vms"):
                    continue
                # chọn VM CPU cao nhất
                vm_to_migrate = max(detail["vms"], key=lambda v: v["cpu_usage"])
                migrate_vm(vm_to_migrate["uuid"], target_host)

        Logger.info(f"Step {step} done.\n")       
    Logger.info("Scheduler finished all steps.")
    Logger.info("Scheduler exited.")
if __name__ == "__main__":
    Logger.info("Starting simple scheduler...")
    simple_schedular(max_steps=MAX_STEP)
    Logger.info("Scheduler exited.")

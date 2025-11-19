import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import requests
from simulation.libs import Logger
import requests
from simulation import state

API = "http://127.0.0.1:8000"

CPU_OVERLOAD = 80
CPU_UNDERLOAD = 50
MAX_STEP = 300
POLL_INTERVAL = 0.01  # 10ms

def wait_for_new_step(last_step):
    while True:
        cur = state.timestamp.get("current", 0)
        if cur > last_step:
            return cur
        time.sleep(1)

def wait_for_step_ready(last_step, timeout = None):
    got = state.step_ready_event.wait(timeout=timeout)
    Logger.info("-------------------------Stuck here-------------------------")
    if not got:
        return None
    return state.timestamp.get("current", None)

    
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
    last_step = -1
    Logger.info("============== Starting Simple Scheduler ===============")
    
    for _ in range(max_steps):
        
        # chờ timestamp tăng (từ mô phỏng)
        step = wait_for_step_ready(last_step, timeout=10.0)
        
        
        step = state.timestamp.get("current", -1)
        if step <= last_step:
            # chưa có step mới
            time.sleep(POLL_INTERVAL)
            continue
        
        Logger.info(f"[Scheduler] Handling step {step}")
        last_step = step
        
        Logger.info(f"Scheduler handling step {step}")
        
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

        try:
            if overloaded and underloaded:
                target_host = min(underloaded, key=lambda x: x[1])[0]
                for src_host, _ in overloaded:
                    detail = get_host_detail(src_host)
                    if not detail:
                        continue
                    vms = detail.get("vms", [])
                    if not vms:
                        continue

                    # choose VM by available keys and cpu_usage field (API should return VM cpu as float)
                    def vm_cpu_val(v):
                        val = v.get("cpu_usage")
                        # if cpu_usage is list (unlikely via API), guard access
                        if isinstance(val, list):
                            idx = state.timestamp.get("current", 0)
                            return val[idx] if idx < len(val) else 0.0
                        return val if isinstance(val, (int, float)) else 0.0

                    vm_to_migrate = max(vms, key=vm_cpu_val)
                    vm_uuid = vm_to_migrate.get("uuid") or vm_to_migrate.get("vm_id")
                    if vm_uuid:
                        migrate_vm(vm_uuid, target_host)
                    else:
                        Logger.warning(f"No uuid found for candidate VM on host {src_host}")
            else:
                Logger.info("No migration needed this step.")
        except Exception as e:
            Logger.error(f"Error during scheduling logic: {e}")
        finally:
            # ALWAYS let simulation continue (avoid deadlock)
            state.step_continue_event.set()
            last_step = step
            Logger.info(f"Step {step} done.\n")


        
    Logger.info("Scheduler finished all steps.")

if __name__ == "__main__":
    simple_scheduler(MAX_STEP)

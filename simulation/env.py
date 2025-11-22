from simulation.host import Host
from simulation.libs import Logger
from simulation import state 
import simpy
import time
import requests
import threading

API = "http://127.0.0.1:8000"
MAX_STEP = 300
CPU_OVERLOAD = 80
CPU_UNDERLOAD = 50
POLL_INTERVAL = 0.01

class SimulationEnv:
    def __init__(self, pm_list, api_url = API, max_steps = MAX_STEP):
        self.pm_list = pm_list
        self.api_url = api_url
        self.env = simpy.Environment()
        self.max_steps = max_steps
        self.pause_sim = False
    
    def simulation_process(self):
        
        for t_idx in range(300):
            if t_idx == 0:
                
                # --------------------------------------------
                # STEP 0: khởi tạo VM từ pm["vms"] 
                # --------------------------------------------
                for pm in self.pm_list:
                    pm_id = pm["pm_id"]
                    total_cpu = pm.get("total_cpu", 1)
                    total_memory = pm.get("total_memory", 1)

                    # Host init
                    if pm_id not in state.hosts:
                        host = Host(self.env, 
                                    pm_id, 
                                    total_cpu = total_cpu, 
                                    total_memory = total_memory)
                        state.hosts[pm_id] = host
                        Logger.info(f"[SIM] Init Host {pm_id}")
                    else:
                        host = state.hosts[pm_id]

                    # VM init
                    for vm in pm["vms"]:
                        uuid = vm["vm_id"]
                        cpu_allocated = vm.get("vcpus", 1)
                        memory = vm.get("memory", 1)
                        cpu_usage_list = vm.get("cpu_usage", [])

                        # Lấy giá trị CPU usage theo t_idx nếu có
                        if t_idx < len(cpu_usage_list):
                            cpu_usage = cpu_usage_list[t_idx]
                        else:
                            cpu_usage = 0.0  # hoặc giữ giá trị cũ

                        if uuid not in host.uuid_to_vm:
                            vm_obj = host.add_vm(uuid, 
                                                 cpu_usage = cpu_usage, 
                                                 cpu_steal=0.0, 
                                                 cpu_allocated = cpu_allocated, 
                                                 memory=memory, 
                                                 net_in = 0.0,
                                                 net_out = 0.0, 
                                                 cpu_usage_list = cpu_usage_list)
                            state.vms[uuid] = vm_obj
                            
                        else:
                            vm_obj = host.uuid_to_vm[uuid]
                            vm_obj.update(cpu_usage = cpu_usage, 
                                          cpu_steal=0.0,
                                          cpu_allocated = cpu_allocated, 
                                          memory = memory,
                                          net_in = 0.0, 
                                          net_out = 0.0)
                            state.vms[uuid] = vm_obj
                        state.list_vms.append(vm)
                    host.update_qos_risk()
                    host.update_after_change()
                    
                # Update step
                state.timestamp["current"] = t_idx
                Logger.info(f"[SIM] Step {t_idx} | Hosts: {len(state.hosts)}, VMs: {len(state.vms)}")
                # Notify scheduler
                state.step_ready_event.set()
                
                waited = 0.0
                while waited < 5.0:  # max wait 5s
                    if state.step_continue_event.is_set():
                        break
                    yield self.env.timeout(0.01)
                    waited += 0.01
                state.step_continue_event.wait() 
                # Clear events for next step
                state.step_continue_event.clear()
                state.step_ready_event.clear()

                yield self.env.timeout(1)
                continue
            else:
                # ------------------------------------------------------------------
                # STEP ≥ 1: cập nhật VM từ state.hosts
                # ------------------------------------------------------------------

                for host in state.hosts.values():
                    for uuid, vm_obj in host.uuid_to_vm.items():

                        # Lấy CPU mới từ cpu_usage_list
                        usage_list = vm_obj.cpu_usage_list
                        if t_idx < len(usage_list):
                            new_cpu = usage_list[t_idx]
                        else:
                            new_cpu = vm_obj.cpu_usage  # giữ nguyên

                        vm_obj.update(cpu_usage=new_cpu)
                                        
                    host.update_qos_risk()
                    host.update_after_change()
                    
                # Gửi event step t_idx
                state.timestamp["current"] = t_idx
                Logger.info(f"[SIM] Step {t_idx} | Hosts: {len(state.hosts)}, VMs: {len(state.vms)}")

                state.step_ready_event.set()
                waited = 0.0
                while waited < 5.0:  # max wait 5s
                    if state.step_continue_event.is_set():
                        break
                    yield self.env.timeout(0.01)
                    waited += 0.01
                state.step_continue_event.wait()

                state.step_continue_event.clear()
                state.step_ready_event.clear()

                yield self.env.timeout(1)
                
    def simple_scheduler(self, cpu_overload = CPU_OVERLOAD, cpu_underload = CPU_UNDERLOAD):
        last_step = -1 
        Logger.info("============== Starting Simple Scheduler ===============")
        while not self.pause_sim:
            step = state.timestamp.get("current", -1)
            if step <= last_step:
            # chưa có step mới
                time.sleep(POLL_INTERVAL)
                continue
            
            last_step = step
            Logger.info(f"[Scheduler] Handling step {step}")

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

                if cpu > cpu_overload and num_vms > 0:
                    overloaded.append((hostname, cpu))
                elif cpu < cpu_underload:
                    underloaded.append((hostname, cpu))

            if overloaded and underloaded:
                target_host = min(underloaded, key=lambda x: x[1])[0]
                for src_host, _ in overloaded:
                    detail = requests.get(f"{self.api_url}/hosts/{src_host}").json()
                    if not detail or not detail.get("vms"):
                        continue
                    vm_to_migrate = max(detail["vms"], key=lambda v: v["cpu_usage"])
                    self.migrate_vm(vm_to_migrate["uuid"], target_host)
            
                    
            # Notify simulation to continue
            state.step_continue_event.set()
            
    def migrate_vm(self, vm_uuid, target_host):
        try:
            # Lấy thông tin VM hiện tại từ API trước khi migrate
            vm_info_resp = requests.get(f"{self.api_url}/vm/{vm_uuid}")
            if vm_info_resp.status_code != 200:
                Logger.warning(f"Cannot fetch VM {vm_uuid} info: {vm_info_resp.text}")
                return

            vm_info = vm_info_resp.json()
            current_host = vm_info.get("host")

            # Nếu VM đã ở host đích thì không migrate
            if current_host == target_host:
                Logger.info(f"VM {vm_uuid} already on target host {target_host}, skipping migration")
                return

            # Gọi API migrate
            payload = {"uuid": vm_uuid, "des_host": str(target_host)}
            r = requests.post(f"{self.api_url}/migrate", json=payload)

            if r.status_code == 200:
                Logger.succeed(f"Migrated VM {vm_uuid} -> Host {target_host}")
            elif r.status_code == 400:
                Logger.info(f"VM {vm_uuid} migration skipped: {r.json().get('detail')}")
            else:
                Logger.warning(f"Migration failed: {r.json()}")
        except Exception as e:
            Logger.error(f"Error calling migrate API for VM {vm_uuid}: {e}")
        vm = state.vms[vm_uuid]
        step = state.timestamp.get("current", -1)
        print(f"[DEBUG] Step after migrate: {step}")
        print(f"hostname of {vm_uuid} is {vm.hostname}")
   
    # -------------------- Run simulation --------------------
    def run(self):
        # Start scheduler in thread
        sched_thread = threading.Thread(target=self.simple_scheduler, daemon=True)
        sched_thread.start()
        # Run SimPy environment
        self.env.process(self.simulation_process())
        self.env.run()
        Logger.info("[SIM] Simulation finished")
        self.pause_sim = True
               

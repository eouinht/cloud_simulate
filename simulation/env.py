from simulation.host import Host
from data.utils import safe_float, safe_list_parse, parse_set_string
from simulation.observe import inspect_host
from simulation.libs import Logger
from simulation import state 
import time 

        
def simulation_process(env, df):
    """
    env: môi trường SimPy
    df: pandas DataFrame có cấu trúc:
        pm_id, t_idx, threshold, total_cpu, total_memory,
        vm_set, vcpus_set, memory_set, cpu_usage_set
    """
    for t, df_t in df.groupby("t_idx"):   # thay timestamp -> t_idx
        
        Logger.info(f"Time {t}")
        
        state.timestamp["current"] = t
        Logger.info(f"check time hereeeeeeeee {state.timestamp}")
        
        for _, row in df_t.iterrows():
            hostname = row["pm_id"]
            if hostname not in state.hosts:
                Logger.info(f"Bắt đầu khởi tạo host: {hostname}")
                
                total_cpu = float(row.get("total_cpu", 1))
                total_memory = float(row.get("total_memory", 1))
                cpu_usage = float(row.get("cpu_usage", 0))  # nếu dataset không có, mặc định 0
                # threshold = float(row.get("threshold", 0.7))  # nếu muốn lưu threshold
                
                host = Host(env,
                            hostname,
                            total_cpu=total_cpu,
                            cpu_usage=cpu_usage,
                            total_memory=total_memory)
                
                # host.threshold = threshold  # thêm trường threshold nếu Host chưa có
                state.hosts[hostname] = host

            else:
                host = state.hosts[hostname]


            # --- Parse dữ liệu VM ---
            
            uuid_set     = parse_set_string(row["vm_set"])
            
            vm_vcpus     = parse_set_string(row["vcpus_set"])
            vm_memory    = parse_set_string(row["memory_set"])
            vm_cpu_usage = parse_set_string(row["cpu_usage_set"])

            num_vms = min(len(uuid_set), len(vm_cpu_usage))

            # --- Cập nhật hoặc thêm mới VM ---
            for i in range(num_vms):
                
                uuid = uuid_set[i]
                cpu_usage = safe_float(vm_cpu_usage[i])
                cpu_allocated =  safe_float(vm_vcpus[i])
                memory = safe_float(vm_memory[i])
                cpu_steal = 0.0  # không có cột này trong dataset mới
                net_in = 0.0     # không có
                net_out = 0.0    # không có

                if uuid not in host.uuid_to_vm:
                    vm_obj  = host.add_vm(uuid, 
                                          cpu_usage, 
                                          cpu_steal, 
                                          cpu_allocated, 
                                          memory, 
                                          net_in, 
                                          net_out)
                    state.vms[uuid] = vm_obj
                else:
                    vm_obj = host.uuid_to_vm[uuid]
                    vm_obj.update(
                        cpu_usage=cpu_usage,
                        cpu_steal=cpu_steal,
                        cpu_allocated=cpu_allocated,
                        memory = memory,
                        net_in=net_in,
                        net_out=net_out
                    )
                    state.vms[uuid] = vm_obj 

            # --- Cập nhật host CPU usage ---
            # host.update_after_change()
            host.update_qos_risk()
            Logger.info(f"[CHECK] pm={hostname}, vm_set_raw={row['vm_set'][:200]}")
            Logger.info(f"[CHECK] pm={hostname}, uuid_count={len(uuid_set)}")

        Logger.info(f"SimPy time = {env.now}, t_idx = {t}")
        state.timestamp["current"] = env.now
        # inspect_host()
        # Kiểm tra state có đủ host và VM chưa
        Logger.info(f"[DEBUG] Tổng số host hiện tại: {len(state.hosts)}")
        
        # for hname, host in state.hosts.items():
        #     Logger.info(f"  Host: {hname} | Số VM: {len(host.uuid_to_vm)}")
            
        Logger.info(f"[DEBUG] Tổng số VM hiện tại: {len(state.vms)}")

        yield env.timeout(1)  # mỗi t_idx = 1 step
        

        # Logger.info("Here")


def simulation_process_json(env, pm_list):
    """
    env: SimPy environment
    json_data: list of PMs
    pm_list: list of PM dicts, mỗi dict có keys: pm_id, total_cpu, total_memory, threshold, vms

    """
    max_steps = max(len(vm["cpu_usage"]) for pm in pm_list for vm in pm["vms"])
    
    for t_idx in range(max_steps):
        for pm in pm_list:
            pm_id = pm["pm_id"]
            total_cpu = pm.get("total_cpu", 1)
            total_memory = pm.get("total_memory", 1)

            # Khởi tạo host nếu chưa có
            if pm_id not in state.hosts:
                host = Host(env, pm_id, total_cpu=total_cpu, total_memory=total_memory)
                state.hosts[pm_id] = host
                Logger.info(f"[SIM] Khởi tạo Host {pm_id}")
            else:
                host = state.hosts[pm_id]

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
                    vm_obj = host.add_vm(uuid, cpu_usage=cpu_usage, cpu_steal=0.0,
                                         cpu_allocated=cpu_allocated, memory=memory,
                                         net_in=0.0, net_out=0.0)
                    state.vms[uuid] = vm_obj
                else:
                    vm_obj = host.uuid_to_vm[uuid]
                    vm_obj.update(cpu_usage=cpu_usage, cpu_steal=0.0,
                                  cpu_allocated=cpu_allocated, memory=memory,
                                  net_in=0.0, net_out=0.0)
                    state.vms[uuid] = vm_obj

            host.update_qos_risk()

        state.timestamp["current"] = t_idx
        Logger.info(f"[SIM] SimPy time = {env.now}, t_idx = {t_idx}, hosts={len(state.hosts)}, vms={len(state.vms)}")
        yield env.timeout(1)  # mỗi step SimPy
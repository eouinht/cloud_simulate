from simulation.host import Host
from data.utils import safe_float, safe_list_parse, parse_set_string
from simulation.observe import inspect_host
from simulation.libs import Logger
from simulation import state 
import time 

# def simulation_process(env, df):
#     """
#         env: môi trường SimPy
#         df: pandas DataFrame
#     """
#     for t, df_t in df.groupby("timestamp"):
#     # for t, df_t in df.groupby("t_idx"):   
        
        
#         # env.run(until=10)
#         # print(f"\n Time {t}")
        
#         for _, row in df_t.iterrows():
#             # hostname = row["hostname"]
#             hostname = row["pm_id"]

#             # Nếu host chưa tồn tại thì khởi tạo
#             if hostname not in state.hosts:
#                 Logger.info(f"Bắt đầu khởi tạo host: {hostname}")
#                 cpu_usage = row.get("cpu_usage", 0.0)
#                 state.hosts[hostname] = Host(env, hostname, cpu_usage)
#             host = state.hosts[hostname]
#             # state.hosts_this_step.add(hostname)

#             # --- Parse dữ liệu VM ---
#             vm_cpu_steal     = safe_list_parse(row["vm_cpu_steal"])
#             vm_cpu_usage     = safe_list_parse(row["vm_cpu_usage"])
#             vm_cpu_allocated = safe_list_parse(row["vm_cpu_allocated"])
#             vm_network_in    = safe_list_parse(row["vm_network_in"])
#             vm_network_out   = safe_list_parse(row["vm_network_out"])
#             uuid_set         = safe_list_parse(row["uuid_set"])
            
#             num_vms = min(
#                 len(uuid_set),
#                 len(vm_cpu_steal),
#                 len(vm_cpu_usage),
#                 len(vm_cpu_allocated),
#                 len(vm_network_in),
#                 len(vm_network_out),
#             )

#             # # --- Xóa VM không còn tồn tại ---
#             # for uuid in list(host.uuid_to_vm.keys()):
#             #     if uuid not in uuid_set:
#             #         host.remove_vm(uuid)
#             #         Logger.succeed("Xóa VM khỏi host thành công.")

#             # --- Cập nhật hoặc thêm mới VM ---
#             for i in range(num_vms):
#                 uuid = uuid_set[i]
#                 cpu_steal = safe_float(vm_cpu_steal[i])
#                 cpu_usage = safe_float(vm_cpu_usage[i])
#                 cpu_allocated = safe_float(vm_cpu_allocated[i])
#                 net_in = safe_float(vm_network_in[i])
#                 net_out = safe_float(vm_network_out[i])

#                 if uuid not in host.uuid_to_vm:
#                     # Logger.info(f"Thêm {uuid} mới vào {host.uuid_to_vm}")
#                     # Thêm mới VM
#                     # vm = VM(env, hostname, uuid, steal, usage, alloc, netin, netout)
#                     host.add_vm( uuid, cpu_usage, cpu_steal, cpu_allocated, net_in, net_out)
#                     state.vms[uuid] = {"host":hostname}
#                 else:
#                     # Cập nhật VM
#                     host.uuid_to_vm[uuid].update(
#                         cpu_usage=cpu_usage,
#                         cpu_steal=cpu_steal,
#                         cpu_allocated=cpu_allocated,
#                         net_in=net_in,
#                         net_out=net_out)
#                     state.vms[uuid]["host"] = hostname
#                 # Logger.succeed(f"Them VM {uuid} vao {host.uuid_to_vm}")
                
#             # --- Cập nhật host CPU usage ---         
#             host.update_after_change()
           
#         Logger.info(f"Time {t}")
#         state.timestamp["current"] = t
#         inspect_host(state.hosts)
#         # time.sleep(1)
#         yield env.timeout(1)  # mỗi timestamp = 1 step
        
def simulation_process(env, df):
    """
    env: môi trường SimPy
    df: pandas DataFrame có cấu trúc:
        pm_id, t_idx, threshold, total_cpu, total_memory,
        vm_set, vcpus_set, memory_set, cpu_usage_set
    """
    for t, df_t in df.groupby("t_idx"):   # thay timestamp -> t_idx
        for _, row in df_t.iterrows():
            hostname = row["pm_id"]
            

            # Nếu host chưa tồn tại thì khởi tạo
            if hostname not in state.hosts:
                total_cpu = float(row.get("total_cpu", 1))
                Logger.info(f"Bắt đầu khởi tạo host: {hostname}")
                cpu_usage = 0.0  # không có trong dataset mới
                state.hosts[hostname] = Host(env, 
                                             hostname,
                                             total_cpu, 
                                             cpu_usage)
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
                cpu_steal = 0.0  # không có cột này trong dataset mới
                net_in = 0.0     # không có
                net_out = 0.0    # không có

                if uuid not in host.uuid_to_vm:
                    host.add_vm(uuid, cpu_usage, cpu_steal, cpu_allocated, net_in, net_out)
                    state.vms[uuid] = {"host": hostname}
                else:
                    host.uuid_to_vm[uuid].update(
                        cpu_usage=cpu_usage,
                        cpu_steal=cpu_steal,
                        cpu_allocated=cpu_allocated,
                        net_in=net_in,
                        net_out=net_out
                    )
                    state.vms[uuid]["host"] = hostname

            # --- Cập nhật host CPU usage ---
            host.update_after_change()

        Logger.info(f"Time {t}")
        state.timestamp["current"] = t
        inspect_host(state.hosts)
        # Kiểm tra state có đủ host và VM chưa
        Logger.info(f"[DEBUG] Tổng số host hiện tại: {len(state.hosts)}")
        for hname, host in state.hosts.items():
            Logger.info(f"  Host: {hname} | Số VM: {len(host.uuid_to_vm)}")
            
        Logger.info(f"[DEBUG] Tổng số VM hiện tại: {len(state.vms)}")

        yield env.timeout(1)  # mỗi t_idx = 1 step
        time.sleep(60)

        Logger.info("Here")
import ast
from simulation.host import Host
import random 
import math
import numpy as np
import json
from simulation.vm import VM
from simulation.observe import inspect_host
from simulation.libs import Logger
from simulation import state 
# from observe import pause_and_inspect, wait_for_pause_signal

# Globla state

def safe_list_parse(value):
    """Chuyển chuỗi list thành list an toàn, nếu lỗi thì trả về list rỗng."""
    if isinstance(value, list):
        return value
    if value is None or value == "" or str(value).lower() == "nan":
        return []
    try:
        # chuẩn hóa chuỗi trước khi eval
        val = str(value).replace("nan", "0").replace("NaN", "0")
        return ast.literal_eval(val)
    except Exception as e:
        Logger.error("Parse error:", value, e)  # debug
        return []

def safe_float(x):
    """Chuyển về float, thay NaN hoặc lỗi thành 0."""
    try:
        val = float(x)
        if np.isnan(val):
            return 0.0
        return val
    except Exception:
        return 0.0

def simulation_process(env, df):
    """
        env: môi trường SimPy
        df: pandas DataFrame
    """
   
        
    for t, df_t in df.groupby("timestamp"):
        # env.run(until=10)
        # print(f"\n Time {t}")
        
        for _, row in df_t.iterrows():
            hostname = row["hostname"]

            # Nếu host chưa tồn tại thì khởi tạo
            if hostname not in state.hosts:
                Logger.info(f"Bắt đầu khởi tạo host: {hostname}")
                host_cpu_usage = row.get("host_cpu_usage", 0.0)
                state.hosts[hostname] = Host(env, hostname, host_cpu_usage)
            host = state.hosts[hostname]
            # state.hosts_this_step.add(hostname)

            # --- Parse dữ liệu VM ---
            vm_cpu_steal     = safe_list_parse(row["vm_cpu_steal"])
            vm_cpu_usage     = safe_list_parse(row["vm_cpu_usage"])
            vm_cpu_allocated = safe_list_parse(row["vm_cpu_allocated"])
            vm_network_in    = safe_list_parse(row["vm_network_in"])
            vm_network_out   = safe_list_parse(row["vm_network_out"])
            uuid_set         = safe_list_parse(row["uuid_set"])

            num_vms = min(
                len(uuid_set),
                len(vm_cpu_steal),
                len(vm_cpu_usage),
                len(vm_cpu_allocated),
                len(vm_network_in),
                len(vm_network_out),
            )

            # # --- Xóa VM không còn tồn tại ---
            # for uuid in list(host.uuid_to_vm.keys()):
            #     if uuid not in uuid_set:
            #         host.remove_vm(uuid)
            #         Logger.succeed("Xóa VM khỏi host thành công.")

            # --- Cập nhật hoặc thêm mới VM ---
            for i in range(num_vms):
                uuid = uuid_set[i]
                cpu_steal = safe_float(vm_cpu_steal[i])
                cpu_usage = safe_float(vm_cpu_usage[i])
                cpu_allocated = safe_float(vm_cpu_allocated[i])
                net_in = safe_float(vm_network_in[i])
                net_out = safe_float(vm_network_out[i])

                if uuid not in host.uuid_to_vm:
                    # Logger.info(f"Thêm {uuid} mới vào {host.uuid_to_vm}")
                    # Thêm mới VM
                    # vm = VM(env, hostname, uuid, steal, usage, alloc, netin, netout)
                    host.add_vm( uuid, cpu_usage, cpu_steal, cpu_allocated, net_in, net_out)
                    state.vms[uuid] = {"host":hostname}
                else:
                    # Cập nhật VM
                    host.uuid_to_vm[uuid].update(
                        cpu_usage=cpu_usage,
                        cpu_steal=cpu_steal,
                        cpu_allocated=cpu_allocated,
                        net_in=net_in,
                        net_out=net_out)
                    state.vms[uuid]["host"] = hostname
                # Logger.succeed(f"Them VM {uuid} vao {host.uuid_to_vm}")
            # --- Cập nhật host CPU usage ---         
            # host.update_host_cpu_usage()
            host.update_after_change()
             # ✅ In ra thử state hiện tại
            # print(f"\n===== STATE at time {t} =====")
            # for hn, h in state.hosts.items():
            #     print(f"Host {hn}, cpu={h.host_cpu_usage}, vms={list(h.uuid_to_vm.keys())}")

        Logger.info(f"Time {t}")
        state.timestamp = t
        # draw_state.hosts_bars(state.hosts)
        inspect_host(state.hosts)
        # print("=== Hosts after simulation ===")
        # for hn, h in state.hosts.items():
        #     print(f"Host {hn} | CPU: {h.host_cpu_usage} | VMs: {list(h.uuid_to_vm.keys())}")

        # print("=== VMs ===")
        # for vm, info in state.vms.items():
        #     print(f"VM {vm} on host {info['host']}")

        yield env.timeout(1)  # mỗi timestamp = 1 step
        
        # return state.hosts
            
# def step_simulation(env, df, state.hosts, step):
#     """
#     Perform one step of the simulation.
#     env: SimPy environment
#     df: pandas DataFrame containing data
#     hosts: dictionary {hostname: Host}
#     step: current simulation step index
#     """
#     df_t = df[df["timestamp"] == step]
#     if df_t.empty:
#         Logger.warning(f"No data for step {step}")
#         return hosts

#     for _, row in df_t.iterrows():
#         hostname = row["hostname"]

#         # Create host if not exist
#         if hostname not in hosts:
#             Logger.info(f"Initializing new host: {hostname}")
#             host_cpu_usage = row.get("host_cpu_usage", 0.0)
#             hosts[hostname] = Host(env, hostname, host_cpu_usage)
#         host = hosts[hostname]

#         # --- Parse VM data ---
#         vm_cpu_steal     = safe_list_parse(row["vm_cpu_steal"])
#         vm_cpu_usage     = safe_list_parse(row["vm_cpu_usage"])
#         vm_cpu_allocated = safe_list_parse(row["vm_cpu_allocated"])
#         vm_network_in    = safe_list_parse(row["vm_network_in"])
#         vm_network_out   = safe_list_parse(row["vm_network_out"])
#         uuid_set         = safe_list_parse(row["uuid_set"])

#         num_vms = min(
#             len(uuid_set),
#             len(vm_cpu_steal),
#             len(vm_cpu_usage),
#             len(vm_cpu_allocated),
#             len(vm_network_in),
#             len(vm_network_out),
#         )

#         for i in range(num_vms):
#             uuid = uuid_set[i]
#             cpu_steal = safe_float(vm_cpu_steal[i])
#             cpu_usage = safe_float(vm_cpu_usage[i])
#             cpu_allocated = safe_float(vm_cpu_allocated[i])
#             net_in = safe_float(vm_network_in[i])
#             net_out = safe_float(vm_network_out[i])

#             if uuid not in host.uuid_to_vm:
#                 host.add_vm(uuid, cpu_usage, cpu_steal, cpu_allocated, net_in, net_out)
#             else:
#                 host.uuid_to_vm[uuid].update(
#                     cpu_usage=cpu_usage,
#                     cpu_steal=cpu_steal,
#                     cpu_allocated=cpu_allocated,
#                     net_in=net_in,
#                     net_out=net_out
#                 )

#         host.update_after_change()

#     Logger.info(f"Step {step} completed.")
#     inspect_host(hosts)
#     return hosts


# def create_simulation_env(simpy_env, df):
#     """
#     Create a callable simulation runner.
#     Returns a function that advances simulation step-by-step.
#     """
#     hosts = {}
#     current_step = {"value": 0}  # use dict for mutability

#     def run_one_step():
#         step_simulation(simpy_env, df, hosts, current_step["value"])
#         current_step["value"] += 1
#         simpy_env.timeout(1)

#     return run_one_step, hosts
            
import ast
from host import Host
import random 
import math
import numpy as np
import json
from vm import VM
from observe import inspect_host
from libs import Logger
# from observe import pause_and_inspect, wait_for_pause_signal
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
    hosts = {}

    for t, df_t in df.groupby("timestamp"):
        # env.run(until=10)
        # print(f"\n Time {t}")
        for _, row in df_t.iterrows():
            hostname = row["hostname"]

            # Nếu host chưa tồn tại thì khởi tạo
            if hostname not in hosts:
                Logger.info(f"Bắt đầu khởi tạo host: {hostname}")
                host_cpu_usage = row.get("host_cpu_usage", 0.0)
                hosts[hostname] = Host(env, hostname, host_cpu_usage)
            host = hosts[hostname]
            # hosts_this_step.add(hostname)

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
                else:
                    # Cập nhật VM
                    host.uuid_to_vm[uuid].update(
                        cpu_usage=cpu_usage,
                        cpu_steal=cpu_steal,
                        cpu_allocated=cpu_allocated,
                        net_in=net_in,
                        net_out=net_out)

                # Logger.succeed(f"Them VM {uuid} vao {host.uuid_to_vm}")
            # --- Cập nhật host CPU usage ---         
            # host.update_host_cpu_usage()
            host.update_after_change()
        Logger.info(f"Time {t}")
        # draw_hosts_bars(hosts)
        inspect_host(hosts)
        yield env.timeout(1)  # mỗi timestamp = 1 step
            
        
            
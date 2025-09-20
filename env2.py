import simpy
import pandas as pd
import ast
import numpy as np

# Data preprocessing
# Load and process the CSV file
print("Loading and processing CSV file...")
df = pd.read_csv("/home/thuong/data/merged_output/grouped_metrics_2024-09-01.csv")


# Hàm chuyển đổi chuỗi list thành list Python và thay thế NaN bằng 0
def parse_and_fill_list(s):
    try:
        lst = ast.literal_eval(s)
        if isinstance(lst, list):
            return [0 if pd.isna(x) else x for x in lst]
        return []
    except:
        return []
def safe_parse_list(s):
    if isinstance(s, list):
        return s
    try:
        return ast.literal_eval(s)
    except:
        return []
    
# Áp dụng cho các cột chứa list
cols_list = ['vm_cpu_allocated', 'vm_cpu_usage', 'vm_cpu_steal', 'vm_network_in', 'vm_network_out']
print("Đang xử lý các cột:", cols_list)
for col in cols_list:
    df[col] = df[col].apply(parse_and_fill_list)

# Xử lý cột uuid_set (chuyển từ chuỗi sang list)
df['uuid_set'] = df['uuid_set'].apply(safe_parse_list)
df['timestamp'] = pd.to_datetime(df['timestamp'])
print("Hoàn tất xử lý, DataFrame hiện có", len(df), "dòng")

# =====================================
# ========= Class simulation ==========
# =====================================
class VM:
    def __init__(self, env, hostname, uuid, steal, cpu_usage, cpu_allocated, net_in, net_out):
        self.env = env
        self.hostname = hostname
        self.placemented = False
        self.uuid = uuid
        self.steal = steal
        self.cpu_usage = cpu_usage  # Mức sử dụng CPU hiện tại
        self.cpu_allocated = cpu_allocated  # CPU được cấp phát
        self.net_in = net_in
        self.net_out = net_out

    def is_vm_active(self):
        """
        Kiểm tra xem VM có đang hoạt động hay không.
        """
        if self.cpu_usage is None:
            return False
        # Giả sử nếu CPU usage > 0 thì VM đang hoạt động
        return self.cpu_usage > 0

class Host:
    def __init__(self, hostname, host_cpu_usage):
        self.hostname = hostname
        self.host_cpu_usage = host_cpu_usage
        self.vms = []
        self.uuid_to_vm = {}

    def add_vm(self, vm):
        self.vms.append(vm)
        self.uuid_to_vm[vm.uuid] = vm

    def remove_vm(self, uuid):
        self.vms = [vm for vm in self.vms if vm.uuid != uuid]
        self.uuid_to_vm.pop(uuid, None)

    def get_active_vm_uuids(self):
        return list(self.uuid_to_vm.keys())

    def update_host_cpu_usage(self):
        """
        Cập nhật mức sử dụng CPU của host dựa trên các VM đang hoạt động.

        """
        self.host_cpu_usage = sum(vm.cpu_usage for vm in self.vms if vm.cpu_usage is not None)
        
    def get_top_vms_by_cpu(self, top_n=10):
        return sorted(self.vms, key=lambda vm: vm.cpu_usage or 0, reverse=True)[:top_n]

def simulation_process(env, df, hosts_by_name):
    all_timestamps = sorted(df['timestamp'].unique())

    # ===== Khởi tạo host =====
    unique_hosts = df['hostname'].unique()
    for hostname in unique_hosts:
        if hostname not in hosts_by_name:
            hosts_by_name[hostname] = Host(hostname, host_cpu_usage=0)

    previous_vms_by_uuid = {hostname: set() for hostname in unique_hosts}

    for t in all_timestamps:
        print(f"\n=== Time {t} (sim time = {env.now}) ===")
        df_t = df[df['timestamp'] == t]

        for _, row in df_t.iterrows():
            hostname = row['hostname']
            uuid_set = row['uuid_set']
            vm_cpu_usage = row['vm_cpu_usage']
            vm_cpu_allocated = row['vm_cpu_allocated']
            vm_cpu_steal = row['vm_cpu_steal']
            vm_network_in = row['vm_network_in']
            vm_network_out = row['vm_network_out']

            if not uuid_set or not vm_cpu_usage or not vm_cpu_allocated:
                print(f"Bỏ qua dòng {row.name} vì thiếu dữ liệu")
                continue

            host = hosts_by_name[hostname]
            current_vms = set(uuid_set)
            previous_vms = previous_vms_by_uuid[hostname]

            # Thêm VM mới
            for i, uuid in enumerate(uuid_set):
                if uuid not in host.uuid_to_vm:
                    vm = VM(
                        env, hostname, uuid,
                        steal=vm_cpu_steal[i] if i < len(vm_cpu_steal) else 0,
                        cpu_usage=vm_cpu_usage[i] if i < len(vm_cpu_usage) else 0,
                        cpu_allocated=vm_cpu_allocated[i] if i < len(vm_cpu_allocated) else 0,
                        net_in=vm_network_in[i] if i < len(vm_network_in) else 0,
                        net_out=vm_network_out[i] if i < len(vm_network_out) else 0
                    )
                    host.add_vm(vm)
                    #print(f"Tạo mới VM {uuid} trên host {hostname} với CPU allocated {vm.cpu_allocated}")

            # Cập nhật CPU usage
            for i, uuid in enumerate(uuid_set):
                if uuid in host.uuid_to_vm:
                    usage = vm_cpu_usage[i] if i < len(vm_cpu_usage) else 0
                    host.uuid_to_vm[uuid].cpu_usage = usage
                    print(f"Cập nhật CPU usage của VM {uuid} trên host {hostname} thành {usage}")

            # Xoá VM không còn hoạt động
            removed_vms = previous_vms - current_vms
            for uuid in removed_vms:
                host.remove_vm(uuid)
                print(f"Xoá VM {uuid} khỏi host {hostname}")
                
            # Kiem tra muc su dung CPU hien tai
            
                

            previous_vms_by_uuid[hostname] = current_vms

        yield env.timeout(1)

# Main simulation setup
env = simpy.Environment()
hosts_by_name = {}
env.process(simulation_process(env, df, hosts_by_name))
print("Bắt đầu mô phỏng...")
env.run()
print("Mô phỏng hoàn tất.")
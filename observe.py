import matplotlib.pyplot as plt
import os
from libs import Logger

WARNING_TEXT = '\x1b[33m'
RESET_TEXT = '\x1b[0m'
# def draw_hosts_bars(hosts):
#     os.system('cls' if os.name == 'nt' else 'clear')
#     print("=== Host CPU  usage Overview ===\n")
#     bar_len = 40 # So ky tu cua thanh ngang
#     for hostname, host in hosts.items():
#         usage_percent = host.host_cpu_usage
#         Clamped_usage = max(0, min(usage_percent, 100))
#         filled_len = int(bar_len * usage_percent /100)
#         bar = '█' * filled_len + '-' *(bar_len - filled_len)
#         print(f"{hostname:20s} | {bar}|{usage_percent:6.2f}%")

def find_vm_by_uuid(hosts, search_uuid:str):
    """_summary_ 
    Tìm VM theo UUID hoặc 8 ký tự đầu trong tất cả hosts.
    Trả về tuple (hostname, vm) nếu tìm thấy, None nếu không.
    Args:
        hosts (str): _description_
        search_uuid (str): _description_
    """
    search_uuid = search_uuid.strip().lower()
    for hn, host in hosts.items():
        # print(f"DEBUG host={hn} type={type(host)}")
        # break
        for vm in host.vms:
            if str(vm.uuid).lower().startswith(search_uuid):
                return hn, vm
    return None     
def show_vm_info(hn, vm):
    """_summary_
    Thong tin chi tiet cua mot VM
    """
    Logger.succeed(f"Host={hn}, VM={vm.uuid[:]},  "
                    f"CPU={vm.cpu_usage:.2f}, "
                    f"Alloc={vm.cpu_allocated:.2f}, "
                    f"Steal={vm.vm_cpu_steal:.2f}")
def inspect_host(hosts):
    """
    Cho phép người dùng quan sát:
    - Nhấn 'p': chọn host và xem danh sách VM trong host đó
    - Nhấn 'd': xem top 20 VM có CPU usage cao nhất toàn hệ thống
    - Nhấn 'u': nhập UUID để xem chi tiết VM bất kỳ
    """
    if not hosts:
        Logger.warning("Không có host nào trong hệ thống")
        return 
    
    hostnames = list(hosts.keys())
    Logger.info("DANH SACH HOST")
    # print("\n=== Danh sách host ===")
    for idx, hn in enumerate(hostnames):
        Logger.info(f"[{idx}] {hn} (CPU={hosts[hn].host_cpu_usage:.2f})")
        
    # Logger.warning("Nhấn 'p': chọn host và xem danh sách VM trong host đó")
    # Logger.warning("Nhấn 'd': xem top 20 VM có CPU usage cao nhất toàn hệ thống")
    # Logger.warning("Nhấn 'u': nhập UUID để xem chi tiết VM bất kỳ")
    # Logger.warning("Nhấn 'Enter' để tiếp tục mô phỏng")
    Logger.warning(
    "Lựa chọn: [p] Host → xem VM, [d] Top 20 VM, [u] UUID → chi tiết VM, [Enter] bỏ qua"
    )
    choice = input("Lựa chọn: ").strip().lower()
    if choice == 'p':
        Logger.succeed("Bạn đã chọn 'p' → Chọn host để xem danh sách VM.")
    elif choice == 'd':
        Logger.succeed("Bạn đã chọn 'd' → Xem top 20 VM có CPU usage cao nhất.")
    elif choice == 'u':
        Logger.succeed("Bạn đã chọn 'u' → Nhập UUID để xem chi tiết VM.")
    elif choice == '':
        Logger.succeed("Đã chọn 'Enter', tiếp tục mô phỏng.")
    else:
        Logger.error(f"Lựa chọn không hợp lệ: {choice}")

    # --- d: hiển thị top 20 VM ---
    if choice == "d":
        all_vms = []
        for hostname, host in hosts.items():
            for vm in host.vms:
                all_vms.append((hostname, vm))
        
        if not all_vms:
            Logger.warning("Không có VM nào trong hệ thống.")
            return
        
        top_vms = sorted(all_vms, key=lambda x: x[1].cpu_usage, reverse=True)[:20]
        
        Logger.info("Top 20 VM có CPU usage cao nhất")
        for hn, vm in top_vms:
            Logger.info(f"Host={hn}, VM={vm.uuid[:]}, "
                  f"CPU={vm.cpu_usage:.2f}, "
                  f"Alloc={vm.cpu_allocated:.2f}, "
                  f"Steal={vm.vm_cpu_steal:.2f}")
            
        input(f"{WARNING_TEXT}Nhấn Enter để tiếp tục mô phỏng...")
        
        return

    # --- p: yêu cầu người dùng chọn host ---
    if choice == "p":
        host_idx = input("Nhập thứ tự host: ").strip()
        if not host_idx.isdigit():
            Logger.error("Nhập không hợp lệ, phải là số.")
            return
        idx = int(host_idx)
        if idx < 0 or idx >= len(hostnames):
            Logger.error("Số host không hợp lệ.")
            return
        selected_host = hosts[hostnames[idx]]
        Logger.info(f"\n=== VMs trên host {selected_host.hostname} ===")
        if not selected_host.vms:
            Logger.warning("Host này không có VM nào.")
        else:
            for vm in selected_host.vms:
                Logger.info(f"  VM {vm.uuid[:8]}: "
                      f"CPU={vm.cpu_usage:.2f}, "
                      f"Alloc={vm.cpu_allocated:.2f}, "
                      f"Steal={vm.vm_cpu_steal:.2f}")
                
        input(f"{WARNING_TEXT}Nhấn Enter để tiếp tục mô phỏng...")
        
    if choice == "u":
        
        search_uuid = input(f"{WARNING_TEXT}Nhap UUID hoac 8 ky tu dau de tim: ").strip().lower()
        result = find_vm_by_uuid(hosts, search_uuid) 
        if result is None:
            Logger.error("Không tìm thấy VM với UUID bắt đầu bằng '{search_uuid}.")
        else:
            hn, vm = result
            show_vm_info(hn, vm)
            # Hỏi người dùng có muốn migrate VM này không
            choice_mig = input(f"{WARNING_TEXT}Bạn có muốn migrate VM này không? (y/N): {RESET_TEXT}").strip().lower()
            if choice_mig == "y":
                # Liệt kê host để người dùng dễ chọn
                Logger.info("Danh sách host hiện có:")
                for name in hosts.keys():
                    Logger.normal(f"- {name}")

                # Người dùng tự nhập host đích
                target_host_name = input(f"{WARNING_TEXT}Nhập tên host đích: {RESET_TEXT}").strip()

                if target_host_name not in hosts:
                    Logger.error(f"Host đích '{target_host_name}' không tồn tại.")
                elif target_host_name == hn:
                    Logger.warning("Host đích trùng với host hiện tại — VM sẽ giữ nguyên host.")
                else:
                    migrate_vm(vm.uuid, hosts[hn], hosts[target_host_name])
            input(f"{WARNING_TEXT}Nhấn Enter để tiếp tục mô phỏng...")        
        return 
                       
def observe_hosts(hosts):
    """Show histogram of host CPU usage."""
    if not hosts:
        print("No hosts found!")
        return
    usages = [h.host_cpu_usage for h in hosts.values()]
    plt.hist(usages, bins=10)
    plt.xlabel("Host CPU Usage")
    plt.ylabel("Count")
    plt.title("Host CPU Usage Distribution")
    
    plt.show()

def migrate_vm(vm_uuid:str, src_host, des_host):
    """Migrate a VM from source_host to target_host and update both hosts' CPU usage.


    Args:
        vm_uuid (str): _description_
        src_host (_type_): _description_
        des_host (_type_): _description_
    """
    vm_uuid = vm_uuid.strip().lower()
    
    vm_to_migrate = None
    for uuid, vm in src_host.uuid_to_vm.items():
        if str(uuid).lower().startswith(vm_uuid):
            vm_to_migrate = vm
            vm_uuid = str(uuid)
            break
    if not vm_to_migrate:
        Logger.error(f"Vm {vm_uuid} khong ton tai tren {src_host.hostname}")
        return False
    

    remove_vm = src_host.remove_vm(vm_uuid)
    
    if remove_vm: 
        
        # Gan lai hostname moi cho VM
        remove_vm.hostname = des_host.hostname
        
        # Danh dau co placemented (Da duoc migrate)
        remove_vm.placemented = True
        
        # Cap nhat lai host metric
        des_host.vms.append(remove_vm)
        des_host.uuid_to_vm[vm_uuid] =  remove_vm
        
        # Update CPU 2 host
        # src_host.update_host_cpu_usage()
        # des_host.update_host_cpu_usage()
        src_host.update_after_change()
        des_host.update_after_change()
        
        Logger.succeed( f"Migrated VM {vm_uuid[:8]} từ {src_host.hostname} → {des_host.hostname}")        

        return True
    else:
        Logger.error(f"Không xóa được VM {vm_uuid[:8]} từ host {src_host.hostname}.")
        return False
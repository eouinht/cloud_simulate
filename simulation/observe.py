from simulation.libs import Logger

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
# def inspect_host1(hosts):
#     """
#     Cho phép người dùng quan sát:
#     - Nhấn 'p': chọn host và xem danh sách VM trong host đó
#     - Nhấn 'd': xem top 20 VM có CPU usage cao nhất toàn hệ thống
#     - Nhấn 'u': nhập UUID để xem chi tiết VM bất kỳ
#     """
#     if not hosts:
#         Logger.warning("Không có host nào trong hệ thống")
#         return 
    
#     hostnames = list(hosts.keys())
#     Logger.info("DANH SACH HOST")
#     # print("\n=== Danh sách host ===")
#     # for idx, hn in enumerate(hostnames):
#     #     Logger.info(f"[{idx}] {hn} (CPU={hosts[hn].host_cpu_usage:.2f})")
        
#     Logger.show_hosts_summary(hosts)
#     # Logger.warning("Nhấn 'p': chọn host và xem danh sách VM trong host đó")
#     # Logger.warning("Nhấn 'd': xem top 20 VM có CPU usage cao nhất toàn hệ thống")
#     # Logger.warning("Nhấn 'u': nhập UUID để xem chi tiết VM bất kỳ")
#     # Logger.warning("Nhấn 'Enter' để tiếp tục mô phỏng")
#     Logger.warning(
#     "Lựa chọn: [p] Host → xem VM, [d] Top 20 VM, [u] UUID → chi tiết VM, [Enter] bỏ qua"
#     )
#     choice = input("Lựa chọn: ").strip().lower()
#     if choice == 'p':
#         Logger.succeed("Bạn đã chọn 'p' → Chọn host để xem danh sách VM.")
#     elif choice == 'd':
#         Logger.succeed("Bạn đã chọn 'd' → Xem top 20 VM có CPU usage cao nhất.")
#     elif choice == 'u':
#         Logger.succeed("Bạn đã chọn 'u' → Nhập UUID để xem chi tiết VM.")
#     elif choice == '':
#         Logger.succeed("Đã chọn 'Enter', tiếp tục mô phỏng.")
#     else:
#         Logger.error(f"Lựa chọn không hợp lệ: {choice}")

#     # --- d: hiển thị top 20 VM ---
#     if choice == "d":
#         all_vms = []
#         for hostname, host in hosts.items():
#             for vm in host.vms:
#                 all_vms.append((hostname, vm))
        
#         if not all_vms:
#             Logger.warning("Không có VM nào trong hệ thống.")
#             return
        
#         top_vms = sorted(all_vms, key=lambda x: x[1].cpu_usage, reverse=True)[:20]
        
#         Logger.info("Top 20 VM có CPU usage cao nhất")
#         for hn, vm in top_vms:
#             Logger.info(f"Host={hn}, VM={vm.uuid[:]}, "
#                   f"CPU={vm.cpu_usage:.2f}, "
#                   f"Alloc={vm.cpu_allocated:.2f}, "
#                   f"Steal={vm.vm_cpu_steal:.2f}")
            
#         input(f"{WARNING_TEXT}Nhấn Enter để tiếp tục mô phỏng...")
        
#         return

#     # --- p: yêu cầu người dùng chọn host ---
#     if choice == "p":
#         host_idx = input("Nhập thứ tự host: ").strip()
#         if not host_idx.isdigit():
#             Logger.error("Nhập không hợp lệ, phải là số.")
#             return
#         idx = int(host_idx)
#         if idx < 0 or idx >= len(hostnames):
#             Logger.error("Số host không hợp lệ.")
#             return
#         selected_host = hosts[hostnames[idx]]
#         Logger.info(f"\n=== VMs trên host {selected_host.hostname} ===")
        
#         if not selected_host.vms:
#             Logger.warning("Host này không có VM nào.")
#         else:
#             # for vm in selected_host.vms:
#             #     Logger.info(f"  VM {vm.uuid[:8]}: "
#             #           f"CPU={vm.cpu_usage:.2f}, "
#             #           f"Alloc={vm.cpu_allocated:.2f}, "
#             #           f"Steal={vm.vm_cpu_steal:.2f}")
#             Logger.show_vms_in_host(selected_host.vms)
                
#         input(f"{WARNING_TEXT}Nhấn Enter để tiếp tục mô phỏng...")
        
#     if choice == "u":
        
#         search_uuid = input(f"{WARNING_TEXT}Nhap UUID hoac 8 ky tu dau de tim: ").strip().lower()
#         result = find_vm_by_uuid(hosts, search_uuid) 
#         if result is None:
#             Logger.error("Không tìm thấy VM với UUID bắt đầu bằng '{search_uuid}.")
#         else:
#             hn, vm = result
#             show_vm_info(hn, vm)
#             # Hỏi người dùng có muốn migrate VM này không
#             choice_mig = input(f"{WARNING_TEXT}Bạn có muốn migrate VM này không? (y/N): {RESET_TEXT}").strip().lower()
#             if choice_mig == "y":
#                 # Liệt kê host để người dùng dễ chọn
#                 Logger.info("Danh sách host hiện có:")
#                 for name in hosts.keys():
#                     Logger.normal(f"- {name}")

#                 # Người dùng tự nhập host đích
#                 target_host_name = input(f"{WARNING_TEXT}Nhập tên host đích: {RESET_TEXT}").strip()

#                 if target_host_name not in hosts:
#                     Logger.error(f"Host đích '{target_host_name}' không tồn tại.")
#                 elif target_host_name == hn:
#                     Logger.warning("Host đích trùng với host hiện tại — VM sẽ giữ nguyên host.")
#                 else:
#                     migrate_vm(vm.uuid, hosts[hn], hosts[target_host_name])
#             input(f"{WARNING_TEXT}Nhấn Enter để tiếp tục mô phỏng...")        
#         return 
                       
def inspect_host(hosts):
    """
    Formal host & VM inspection interface.
    Menu-driven with option to go back before continuing simulation.
    """
    if not hosts:
        print("No hosts available.")
        return

    while True:
        print("\n=== HOST SUMMARY ===")
        Logger.show_hosts_summary(hosts)

        print("Options:")
        print("  p - Select a host and list its VMs")
        print("  d - Show top 20 VMs by CPU usage")
        print("  u - Search for VM by UUID")
        print("  c - Continue simulation")
        print("  q - Quit simulation")

        choice = input("Enter choice: ").strip().lower()

        if choice == "p":
            _handle_inspect_host(hosts)
            # After inspecting, loop back to main menu
        elif choice == "d":
            _handle_top_vms(hosts)
        elif choice == "u":
            _handle_search_vm(hosts)
        elif choice == "c":
            print("Continuing simulation...")
            break  # exit the loop → simulation resumes
        elif choice == "q":
            print("Exiting simulation.")
            exit(0)
        elif choice == "":
            print("Press 'c' to continue simulation or choose another option.")
        else:
            print(f"Invalid choice: {choice}")


def _handle_inspect_host(hosts):
    """List VMs in a selected host and return to menu."""
    hostnames = list(hosts.keys())
    for idx, hn in enumerate(hostnames):
        h = hosts[hn]
        print(f"[{idx}] Host={h.hostname} CPU={h.host_cpu_usage:.2f}")

    host_idx = input("Select host index (or press Enter to go back): ").strip()
    if not host_idx:
        return  # go back to main menu

    if not host_idx.isdigit():
        print("Invalid input. Must be a number.")
        return

    idx = int(host_idx)
    if not (0 <= idx < len(hostnames)):
        print("Host index out of range.")
        return

    selected_host = hosts[hostnames[idx]]
    print(f"\n=== VM LIST for Host {selected_host.hostname} ===")
    if not selected_host.vms:
        print("This host has no VMs.")
    else:
        Logger.show_vms_in_host(selected_host.vms)

    input("Press Enter to go back to menu...")


def _handle_top_vms(hosts, top_n=20):
    """Lists top N VMs by CPU usage, then returns to menu."""
    all_vms = [(hn, vm) for hn, host in hosts.items() for vm in host.vms]
    if not all_vms:
        print("No VMs found.")
        return

    top_vms = sorted(all_vms, key=lambda x: x[1].cpu_usage, reverse=True)[:top_n]
    print(f"\n=== TOP {top_n} VMs by CPU usage ===")
    print(f"{'HOST':<15}{'VM UUID':<12}{'CPU':>8}{'ALLOC':>10}{'STEAL':>10}")
    for hn, vm in top_vms:
        print(f"{hn:<15}{vm.uuid[:8]:<12}{vm.cpu_usage:>8.2f}{vm.cpu_allocated:>10.2f}{vm.vm_cpu_steal:>10.2f}")

    input("Press Enter to go back to menu...")


def _handle_search_vm(hosts):
    """Search for a VM by UUID and return to menu."""
    search_uuid = input("Enter UUID or first 8 chars (or Enter to go back): ").strip().lower()
    if not search_uuid:
        return

    result = find_vm_by_uuid(hosts, search_uuid)
    if not result:
        print(f"VM starting with '{search_uuid}' not found.")
        return

    hn, vm = result
    show_vm_info(hn, vm)

    choice_mig = input("Do you want to migrate this VM? (y/N): ").strip().lower()
    if choice_mig == "y":
        print("Available hosts:")
        for name in hosts.keys():
            print(f"- {name}")

        target_host_name = input("Enter destination host (or press Enter to cancel): ").strip()
        if not target_host_name:
            print("Migration canceled.")
        elif target_host_name not in hosts:
            print(f"Target host '{target_host_name}' does not exist.")
        elif target_host_name == hn:
            print("Target host is the same as current. Migration skipped.")
        else:
            migrate_vm(vm.uuid, hosts[hn], hosts[target_host_name])

    input("Press Enter to go back to menu...")


def migrate_vm(vm_uuid: str, src_host, des_host, current_time=None):
    """
    Migrate a VM from a source host to a destination host.

    Args:
        vm_uuid (str): The UUID (or first few characters) of the VM to migrate.
        src_host (Host): Source host object.
        des_host (Host): Destination host object.

    Returns:
        bool: True if migration succeeded, False otherwise.
    """
    vm_uuid = vm_uuid.strip().lower()
    vm_to_migrate = None

    # Find VM in source host
    for uuid, vm in list(src_host.uuid_to_vm.items()):
        if str(uuid).lower().startswith(vm_uuid):
            vm_to_migrate = vm
            vm_uuid = str(uuid)  # normalize full UUID
            break

    if not vm_to_migrate:
        Logger.error(f"VM {vm_uuid} not found on host {src_host.hostname}")
        return False

    Logger.info(f"[DEBUG] Before remove: {len(src_host.vms)} VMs on {src_host.hostname}")

    # Remove VM from source host
    try:
        removed_vm = src_host.remove_vm(vm_uuid)
    except KeyError:
        Logger.error(f"Failed to remove VM {vm_uuid[:8]} from host {src_host.hostname}.")
        return False

    Logger.info(f"[DEBUG] After remove: {len(src_host.vms)} VMs remain on {src_host.hostname}")
    Logger.info(f"[DEBUG] src_host.uuid_to_vm: {list(src_host.uuid_to_vm.keys())}")

    #Change migration status
    removed_vm.migrated = True
    removed_vm.pre_hostname = src_host.hostname
    removed_vm.migrated_time = current_time
    # Add VM to destination host    
    removed_vm.hostname = des_host.hostname
    
    removed_vm.placemented = True  # mark as migrated
    des_host.vms.append(removed_vm)
    des_host.uuid_to_vm[vm_uuid] = removed_vm

    Logger.info(f"[DEBUG] After append: {len(des_host.vms)} VMs on {des_host.hostname}")
    Logger.info(f"[DEBUG] des_host.uuid_to_vm: {list(des_host.uuid_to_vm.keys())}")

    # Update CPU usage for both hosts
    src_host.update_after_change()
    des_host.update_after_change()

    Logger.succeed(f"Migrated VM {vm_uuid[:8]} from {src_host.hostname} → {des_host.hostname}")
    Logger.info(f"[DEBUG] src_host còn {len(src_host.vms)} VM, des_host có {len(des_host.vms)} VM")
    return True

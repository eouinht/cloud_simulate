# observe.py
import re
from simulation import state
from simulation.libs import Logger

def find_vm_by_uuid(search_uuid: str):
    """Tìm VM theo UUID hoặc 8 ký tự đầu trong tất cả hosts."""
    search_uuid = search_uuid.strip().lower()
    for hn, host in state.hosts.items():
        for vm in host.vms:
            if str(vm.uuid).lower().startswith(search_uuid):
                return hn, vm
    return None

def show_vm_info(hn, vm):
    """Hiển thị thông tin chi tiết của VM."""
    Logger.succeed(
        f"Host={hn}, VM={vm.uuid}, "
        f"CPU={vm.cpu_usage:.2f}%, "
        f"Alloc={vm.cpu_allocated:.2f}, "
        f"Steal={vm.vm_cpu_steal:.2f}%"
    )

def migrate_vm(vm_uuid: str, src_host, des_host, current_time=None):
    """Migrate VM từ src_host → des_host"""
    vm_uuid = vm_uuid.strip().lower()
    vm_to_migrate = src_host.uuid_to_vm.get(vm_uuid)
    if not vm_to_migrate:
        Logger.error(f"VM {vm_uuid} not found on host {src_host.hostname}")
        return False

    # Remove VM từ source host
    src_host.vms.remove(vm_to_migrate)
    src_host.uuid_to_vm.pop(vm_uuid)

    # Update migration status
    vm_to_migrate.migrated = True
    vm_to_migrate.pre_hostname = src_host.hostname
    vm_to_migrate.migrated_time = current_time
    vm_to_migrate.hostname = des_host.hostname
    vm_to_migrate.placemented = True

    # Add VM đến destination host
    des_host.vms.append(vm_to_migrate)
    des_host.uuid_to_vm[vm_uuid] = vm_to_migrate

    # Update CPU usage
    src_host.update_after_change()
    des_host.update_after_change()

    Logger.succeed(f"Migrated VM {vm_uuid} from {src_host.hostname} → {des_host.hostname}")
    
    return True

def _handle_inspect_host():
    """List VMs in a selected host."""
    hostnames = list(state.hosts.keys())
    for idx, hn in enumerate(hostnames):
        h = state.hosts[hn]
        print(f"[{idx}] Host={h.hostname} CPU={h.cpu_usage:.2f}%")

    host_idx = input("Select host index (or press Enter to go back): ").strip()
    if not host_idx:
        return
    if not host_idx.isdigit():
        print("Invalid input. Must be a number.")
        return
    idx = int(host_idx)
    if not (0 <= idx < len(hostnames)):
        print("Host index out of range.")
        return

    selected_host = state.hosts[hostnames[idx]]
    print(f"\n=== VM LIST for Host {selected_host.hostname} ===")
    if not selected_host.vms:
        print("This host has no VMs.")
    else:
        Logger.show_vms_in_host(selected_host.vms)

    input("Press Enter to go back to menu...")

def _handle_top_vms(top_n=20):
    """List top N VMs by CPU usage."""
    all_vms = [(hn, vm) for hn, h in state.hosts.items() for vm in h.vms]
    if not all_vms:
        print("No VMs found.")
        return

    top_vms = sorted(all_vms, key=lambda x: x[1].cpu_usage, reverse=True)[:top_n]
    print(f"\n=== TOP {top_n} VMs by CPU usage ===")
    print(f"{'HOST':<15}{'VM UUID':<12}{'CPU':>8}{'ALLOC':>10}{'STEAL':>10}")
    for hn, vm in top_vms:
        print(f"{hn:<15}{vm.uuid[:8]:<12}{vm.cpu_usage:>8.2f}{vm.cpu_allocated:>10.2f}{vm.vm_cpu_steal:>10.2f}")

    input("Press Enter to go back to menu...")

def _handle_search_vm():
    """Search for a VM by UUID and optionally migrate."""
    search_uuid = input("Enter UUID or first 8 chars (or Enter to go back): ").strip()
    if not search_uuid:
        return

    result = find_vm_by_uuid(search_uuid)
    if not result:
        print(f"VM starting with '{search_uuid}' not found.")
        return

    hn, vm = result
    show_vm_info(hn, vm)

    choice_mig = input("Do you want to migrate this VM? (y/N): ").strip().lower()
    if choice_mig != "y":
        return

    print("Available hosts:")
    for name in state.hosts.keys():
        print(f"- {name}")

    target_host_name = input("Enter destination host (or press Enter to cancel): ").strip()
    if not target_host_name:
        print("Migration canceled.")
    else:
        try:
            target_host_idx = int(target_host_name)
        except ValueError:
            print(f"Invalid host: {target_host_name}")
            return

        if target_host_idx not in state.hosts:
            print(f"Target host '{target_host_idx}' does not exist.")
        elif target_host_idx == hn:
            print("Target host is the same as current. Migration skipped.")
        else:
            migrate_vm(vm.uuid, state.hosts[hn], state.hosts[target_host_idx])    
    input("Press Enter to go back to menu...")

def inspect_host():
    """Main CLI menu for host & VM inspection."""
    if not state.hosts:
        print("No hosts available.")
        return

    while True:
        print("\n=== HOST SUMMARY ===")
        Logger.show_hosts_summary(state.hosts)

        print("\nOptions:")
        print("  p - Select a host and list its VMs")
        print("  d - Show top 20 VMs by CPU usage")
        print("  u - Search for VM by UUID")
        print("  c - Continue simulation")
        print("  q - Quit simulation")

        choice = input("Enter choice: ").strip().lower()
        if choice == "p":
            _handle_inspect_host()
        elif choice == "d":
            _handle_top_vms()
        elif choice == "u":
            _handle_search_vm()
        elif choice == "c":
            print("Continuing simulation...")
            break
        elif choice == "q":
            print("Exiting simulation.")
            exit(0)
        else:
            print(f"Invalid choice: {choice}")

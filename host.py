from vm import VM
from libs import Logger
class Host:
    def __init__(self, 
                 env, 
                 hostname, 
                 host_cpu_usage=0.0):
        self.env = env
        self.hostname = hostname
        self.host_cpu_usage = host_cpu_usage
        self.uuid_to_vm = {} # Dict for fast VM lookup
        self.vms = []        # List for iteration
    
    # --- VM management ---    
    def add_vm(self, 
               uuid, 
               cpu_usage, 
               cpu_steal, 
               cpu_allocated, 
               net_in, 
               net_out):
        
        """ Add new VM to the host ( fails if already exists) """
        if uuid in self.uuid_to_vm:
            raise ValueError(f"VM with UUID {uuid} already exists on host {self.hostname}.")
        
        vm = VM(
            env=self.env,
            hostname=self.hostname,
            uuid=uuid,
            vm_cpu_steal=cpu_steal,
            cpu_usage=cpu_usage,
            cpu_allocated=cpu_allocated,
            net_in=net_in,
            net_out=net_out
        )
        self.vms.append(vm)
        self.uuid_to_vm[uuid] = vm
        self.update_host_cpu_usage()
        return vm

    # def update_vm(self, 
    #               uuid, 
    #               cpu_usage=None, 
    #               cpu_steal=None, 
    #               cpu_allocated=None, 
    #               net_in=None, 
    #               net_out=None):
    #     """Update metrics of an existing VM (only provided values are updated)."""
    #     if uuid not in self.uuid_to_vm:
    #         raise KeyError(f"VM {uuid} not found on host {self.hostname}")

    #     vm = self.uuid_to_vm[uuid]
    #     if cpu_usage is not None: vm.cpu_usage = cpu_usage
    #     if cpu_steal is not None: vm.vm_cpu_steal = cpu_steal
    #     if cpu_allocated is not None: vm.cpu_allocated = cpu_allocated
    #     if net_in is not None: vm.net_in = net_in
    #     if net_out is not None: vm.net_out = net_out

    #     self.update_host_cpu_usage()
    #     return vm

    # def add_or_update_vm(self, 
    #                      uuid, 
    #                      cpu_usage, 
    #                      cpu_steal, 
    #                      cpu_allocated, 
    #                      net_in, 
    #                      net_out):
    #     """Add VM if missing, otherwise update metrics."""
    #     if uuid in self.uuid_to_vm:
    #         return self.update_vm(uuid, 
    #                               cpu_usage, 
    #                               cpu_steal, 
    #                               cpu_allocated, 
    #                               net_in, 
    #                               net_out)
    #     else:
    #         return self.add_vm(uuid, 
    #                            cpu_usage, 
    #                            cpu_steal, 
    #                            cpu_allocated, 
    #                            net_in, net_out)

    def remove_vm(self, uuid):
        """Remove a VM from this host."""
        if uuid not in self.uuid_to_vm:
            raise KeyError(f"VM {uuid} not found on host {self.hostname}")
        
        vm = self.uuid_to_vm.pop(uuid)
        self.vms.remove(vm)
        self.update_host_cpu_usage()
        return vm

    # ---------------- Host Stats ---------------- #
    def update_host_cpu_usage(self):
        """Recalculate host CPU usage as sum of all VM usages."""
        self.host_cpu_usage = sum(vm.cpu_usage for vm in self.vms if vm.is_powered_on())
        return self.host_cpu_usage

    def update_after_change(self, debug=False):
        """_Cập nhật CPU usage ngay sau khi có thay đổi về VM (add, remove, migrate).y_

        Args:
            debug (bool, optional): _description_. Defaults to False.
        """
        total = 0.0
        for vm in self.vms:
            if vm.powered_on:
                total += vm.cpu_usage
        self.host_cpu_usage = total
        if debug:
            Logger.info(f"[{self.hostname}] CPU updated after change = {self.host_cpu_usage:.2f}")
        return total
    
    # def get_top_vms_by_cpu(self, top_n=5):
    #     """Return top-N VMs sorted by CPU usage (descending)."""
    #     return sorted(
    #                   (vm for vm in self.vms if vm.is_powered_on()),
    #                   key=lambda vm: vm.cpu_usage, 
    #                   reverse=True
    #                   )[:top_n]

    # def get_vm(self, uuid):
    #     """Get a VM by UUID (None if not found)."""
    #     return self.uuid_to_vm.get(uuid, None)

    # def has_vm(self, uuid):
    #     """Check if VM exists on this host."""
    #     return uuid in self.uuid_to_vm
    # def list_vms(self, powered_only = False):
    #     """Return list of VMs, optionally only powered-on ones."""
    #     if powered_only:
    #         return [vm for vm in self.vms if vm.is_powered_on()]
    #     return self.vms
    

        

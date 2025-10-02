from simulation.vm import VM
from simulation.libs import Logger
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
        self.update_after_change()
        return vm

    def remove_vm(self, uuid):
        """
        Remove a VM from this host (both vms list and uuid_to_vm dict).
        
        Args:
            uuid (str): Full UUID of VM to remove.

        Returns:
            VM: The removed VM object.
        """
        if uuid not in self.uuid_to_vm:
            raise KeyError(f"VM {uuid} not found on host {self.hostname}")
        
        vm = self.uuid_to_vm.pop(uuid)
        # self.vms.remove(vm)
        # self.update_after_change()
        # return vm
        try:
            self.vms.remove(vm)  # remove from list
        except ValueError:
            Logger.warning(f"[DEBUG] VM {uuid[:8]} not found in vms list of {self.hostname}. Dict and list are out of sync!")

        Logger.info(f"[DEBUG] Removed VM {uuid[:8]} from {self.hostname}")
        Logger.info(f"[DEBUG] Remaining VMs on {self.hostname}: {len(self.vms)} (dict keys: {list(self.uuid_to_vm.keys())})")

        self.update_after_change()
        return vm

    # ---------------- Host Stats ---------------- #

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
    
    
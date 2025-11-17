from simulation.vm import VM
from simulation.libs import Logger
class Host:
    def __init__(self, 
                 env, 
                 hostname, 
                 total_cpu = 1.0,
                 cpu_usage = 0.0,
                 total_memory = 0.0,
                 mem_in_used = 0.0,
                 ):
        self.env = env
        self.hostname = hostname
        self.total_cpu = total_cpu
        self.uuid_to_vm = {} # Dict for fast VM lookup
        self.vms = []        # List for iteration
        self.cpu_usage = cpu_usage
        self.total_memory = total_memory
        # self.mem_in_used = mem_in_used
        self.qos_risk = -1
        # --- Logger thông tin khi khởi tạo host ---
        Logger.info(f"[Host Init] Hostname: {self.hostname}")
        Logger.info(f"[Host Init] Total CPU: {self.total_cpu}")
        Logger.info(f"[Host Init] CPU usage: {self.cpu_usage}")
        Logger.info(f"[Host Init] Total Memory: {self.total_memory}")
        # Logger.info(f"[Host Init] Memory in use: {self.mem_in_used}")
        Logger.info(f"[Host Init] QoS Risk: {self.qos_risk}")
        Logger.info(f"[Host Init] VM count: {len(self.vms)}")
        
        
    # --- VM management ---    
    def add_vm(self, 
               uuid, 
               cpu_usage, 
               cpu_steal, 
               cpu_allocated, 
               memory,
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
            memory = memory,
            net_in=net_in,
            net_out=net_out
        )
        self.vms.append(vm)
        self.uuid_to_vm[uuid] = vm
        vm.placemented = True
        self.update_after_change()
        return vm

    def create_vm(self, 
                  uuid = None,
                  cpu_allocated=2.0,
                  memory=2.0,
                  cpu_usage=0.0,
                  vm_cpu_steal=0.0,
                  net_in=0.0,
                  net_out=0.0):
        vm = VM(
            env=self.env,
            uuid = uuid,
            cpu_allocated=cpu_allocated,
            cpu_usage=cpu_usage,
            vm_cpu_steal=vm_cpu_steal,
            net_in=net_in,
            net_out=net_out
        )
        self.vms.append(vm)
        self.uuid_to_vm[vm.uuid] = vm
        vm.placemented = True
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

    # def k_update_after_change(self, debug=False):
    #     """_Cập nhật CPU usage ngay sau khi có thay đổi về VM (add, remove, migrate).y_

    #     Args:
    #         debug (bool, optional): _description_. Defaults to False.
    #     """
    #     total = 0.0
    #     for vm in self.vms:
    #         if vm.powered_on:
    #             total += vm.cpu_usage
    #     self.host_cpu_usage = total
    #     if debug:
    #         Logger.info(f"[{self.hostname}] CPU updated after change = {self.host_cpu_usage:.2f}")
    #     return total
    
    
    def update_after_change(self, debug = False):
        """
        Cập nhật tổng memory đang dùng của host.
        - self.mem_in_used: tổng memory VM đang dùng (GB)
        """
        # Tính tổng memory tất cả VM trên host
        self.mem_in_used= sum(getattr(vm, "memory", 0.0) for vm in self.uuid_to_vm.values())

        if debug:
            print(f"[{self.hostname}] Memory used: {self.memory_used:.3f} GB")

        Logger.info(f"[{self.hostname}] Memory used: {self.mem_in_used:.3f} GB")
        
        if self.mem_in_used > self.total_memory:
            Logger.error("Mem in used > real total mem")
        elif self.mem_in_used  > 0.8*self.total_memory:
            Logger.warning(" The risk of over mem in used to qos theshold")
        
        return self.mem_in_used
   

    def update_qos_risk(self):
        
        self.cpu_usage = sum(
        (getattr(vm, "cpu_usage", 0.0) / 100) * getattr(vm, "cpu_allocated", 1.0)
        for vm in self.uuid_to_vm.values()
        )
        self.cpu_usage = self.cpu_usage*100/self.total_cpu
        self.qos_risk = max(0.0, (self.cpu_usage - 80)/self.cpu_usage)
        
        
        Logger.info(f"[{self.hostname}] Host cpu usage: {self.cpu_usage}")
        Logger.info(f"[{self.hostname}] Qos risk: {self.qos_risk}")
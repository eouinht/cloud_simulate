import pandas as pd
class VM:
    def __init__(self, 
                 env, 
                 hostname, 
                 uuid, 
                 vm_cpu_steal, 
                 cpu_usage, 
                 cpu_allocated, 
                 net_in, 
                 net_out):
        self.env = env
        self.hostname = hostname
        self.placemented = False # VM đã được đặt lên host chưa
        self.uuid = uuid
        # --- VM metrics ---
        self.vm_cpu_steal = float(vm_cpu_steal)
        self.cpu_usage = float(cpu_usage)
        self.cpu_allocated = float(cpu_allocated)
        self.net_in = float(net_in)
        self.net_out = float(net_out)
        # --- Power state(default on) ---
        self.powered_on = True
        
        # --- History for analysis ---
        self.history = {
            "time": [],
            "cpu_steal": [],
            "cpu_usage:": [],
            "cpu_allocated": [],
            "net_in": [],
            "net_out": [],
        }
    def update(self, cpu_usage=None, cpu_steal=None, 
               cpu_allocated=None, net_in=None, net_out=None):
        """Update VM metrics (only provided values are updated)."""
        if cpu_usage is not None: self.cpu_usage = cpu_usage
        if cpu_steal is not None: self.cpu_steal = cpu_steal
        if cpu_allocated is not None: self.cpu_allocated = cpu_allocated
        if net_in is not None: self.net_in = net_in
        if net_out is not None: self.net_out = net_out
        return self
    # def update_metrics(self, timestamp, cpu_steal, cpu_usage, cpu_allocated, net_in, net_out):
    #     # --- Update metric follow time ---
    #     self.cpu_steal = float(cpu_steal)
    #     self.cpu_usage = float(cpu_usage)
    #     self.cpu_allocated = float(cpu_allocated)
    #     self.net_in = float(net_in)
    #     self.net_out = float(net_out)
         
    #     # --- Saving in history --- 
    #     self.history["time"].append(timestamp)
    #     self.history["cpu_steal"].append(cpu_steal)
    #     self.history["cpu_usage:"].append(cpu_usage)
    #     self.history["cpu_allocated"].append(cpu_allocated)
    #     self.history["net_in"].append(net_in)
    #     self.history["net_out"].append(net_out)
        
    # def __repr__(self):
    #     return (f"VM(uuid={self.uuid}, host={self.hostname}, "
    #             f"usage={self.cpu_usage}, alloc={self.cpu_allocated}, "
    #             f"net_in={self.net_in}, net_out={self.net_out})")    
    # # -- Checking power state
    def is_powered_on(self):
        return self.powered_on
    # # --- Power controls ---
    # def power_on(self):
    #     self.powered_on = True
    # def power_off(self):
    #     self.powered_on = False

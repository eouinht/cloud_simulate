import pandas as pd
import uuid as uuid_lib
from .libs import Logger
class VM:
    def __init__(self, 
                 env = None, 
                 uuid = None, 
                 vm_cpu_steal = 0.0, 
                 cpu_usage = 0.0, 
                 cpu_allocated = 0.0, 
                 memory = 0.0,
                 net_in = 0.0, 
                 net_out = 0.0,
                 hostname = None):
        
        self.env = env
        self.uuid = uuid or str(uuid_lib.uuid4())
        self.hostname = hostname
        self.placemented = False # VM đã được đặt lên host chưa
        
        
        # --- VM metrics ---
        self.vm_cpu_steal = vm_cpu_steal
        self.cpu_usage = cpu_usage
        self.cpu_allocated = cpu_allocated
        self.net_in = net_in
        self.net_out = net_out
        self.memory = memory
        # default = False (no migration yet)
        self.migrated = False
        self.pre_hostname = None
        self.migrated_time = None
        # --- Power state(default on) ---
        self.powered_on = True
        
    def assign_host(self, host):     
        # Gan VM vao host
        self.hostname = host.hostname
        self.placemented = True
        
    def migrated_vm(self, tar_host):
        self.pre_hostname = self.hostname
        self.hostname = tar_host.hostname
        self.placemented = True
        self.migrated = True
        if self.env is not None:
            self.migrated_time = self.env.now
        
    def update(self, cpu_usage=None, cpu_steal=None, 
               cpu_allocated=None,memory = None, net_in=None, net_out=None):
        """Update VM metrics (only provided values are updated)."""
        if cpu_usage is not None: self.cpu_usage = cpu_usage
        if cpu_steal is not None: self.cpu_steal = cpu_steal
        if cpu_allocated is not None: self.cpu_allocated = cpu_allocated
        if memory is not None: self.memory = memory
        if net_in is not None: self.net_in = net_in
        if net_out is not None: self.net_out = net_out
        return self
      
    def compute_steal_time(self):
        # fix logic latter
        if self.cpu_allocated <= 0:
            steal_time = 0.0
        else:
            steal_time = max(0.0, (self.cpu_allocated - self.cpu_usage) / self.cpu_allocated * 100.0)
            
        steal_time = round(steal_time, 7)
        self.vm_cpu_steal = steal_time
        Logger.info("Here")
        return steal_time
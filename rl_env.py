import gymnasium as gym
from gymnasium import spaces
import numpy as np
from sim_thuong.simulation.host import Host
from sim_thuong.simulation.vm import VM
from sim_thuong.simulation.libs import Logger
from sim_thuong.simulation.observe import observe_hosts, migrate_vm
from sim_thuong.simulation.env import safe_list_parse, safe_float
def init_hosts_from_df(df, env, step=0, debug=False):
    """
    Khởi tạo hosts từ dataframe ở step cụ thể (dựa trên timestamp).
    
    Args:
        df: pandas DataFrame chứa dữ liệu
        env: SimPy environment
        step: index của timestamp (mặc định = 0)
        debug: in thông tin khi debug
    
    Returns:
        dict {hostname: Host}
    """
    hosts = {}
    timestamps = sorted(df['timestamp'].unique())
    if step >= len(timestamps):
        raise IndexError(f"Step {step} vượt quá số lượng timestamp ({len(timestamps)})")

    current_ts = timestamps[step]
    df_step = df[df['timestamp'] == current_ts]

    if debug:
        Logger.info(f"Khởi tạo hosts từ timestamp={current_ts}")

    for _, row in df_step.iterrows():
        hostname = row["hostname"]
        if hostname not in hosts:
            hosts[hostname] = Host(env, hostname, host_cpu_usage=row.get("host_cpu_usage", 0.0))
        
        # Parse VM data từ hàng hiện tại
        uuid = row["uuid"]
        cpu_usage = row["vm_cpu_usage"]
        cpu_steal = row["vm_cpu_steal"]
        cpu_allocated = row["vm_cpu_allocated"]
        net_in = row["vm_network_in"]
        net_out = row["vm_network_out"]

        hosts[hostname].add_vm(uuid, cpu_usage, cpu_steal, cpu_allocated, net_in, net_out)

    return hosts

def update_hosts_from_df(hosts, df_t, env):
    """
    Cập nhật trạng thái hosts từ một DataFrame của một timestamp cụ thể.
    
    Args:
        hosts (dict): {hostname: Host}
        df_t (pd.DataFrame): Subset của df tại 1 timestamp
        env (simpy.Environment): môi trường mô phỏng
        
    Returns:
        dict: hosts đã được cập nhật
    """
    for _, row in df_t.iterrows():
        hostname = row["hostname"]

        # Nếu host chưa tồn tại thì khởi tạo
        if hostname not in hosts:
            Logger.info(f"Bắt đầu khởi tạo host: {hostname}")
            host_cpu_usage = row.get("host_cpu_usage", 0.0)
            hosts[hostname] = Host(env, hostname, host_cpu_usage)

        host = hosts[hostname]

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

        # --- Cập nhật hoặc thêm mới VM ---
        for i in range(num_vms):
            uuid = uuid_set[i]
            cpu_steal = safe_float(vm_cpu_steal[i])
            cpu_usage = safe_float(vm_cpu_usage[i])
            cpu_allocated = safe_float(vm_cpu_allocated[i])
            net_in = safe_float(vm_network_in[i])
            net_out = safe_float(vm_network_out[i])

            if uuid not in host.uuid_to_vm:
                host.add_vm(uuid, cpu_usage, cpu_steal, cpu_allocated, net_in, net_out)
            else:
                host.uuid_to_vm[uuid].update(
                    cpu_usage=cpu_usage,
                    cpu_steal=cpu_steal,
                    cpu_allocated=cpu_allocated,
                    net_in=net_in,
                    net_out=net_out
                )

        # Cập nhật CPU usage sau khi thay đổi
        host.update_after_change()

    return hosts

class CloudSimEnv(gym.Env):
    def __init__(self, df, num_host):
        super().__init__()
        self.df = df
        self.num_host = num_host
        self.observation_space = spaces.Box(low=0.0, 
                                            high=100.0,
                                            shape=(2*num_host,),
                                            dtype=np.float32)
        self.action_space = spaces.Discrete(num_host)
        self.current_step = 0
        self.hosts = {}
    
    def reset(self, *, seed = None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.hosts = init_hosts_from_df(self.df, step = 0)
        return self.__getstate__(), {}
    def step(self, action):
        # 1. Thực hiện hành động: chọn host để migrate VM nóng nhất
        selected_host = list(self.hosts.values())[action]
        self._migrate_top_vm(selected_host)

        # 2. Chuyển mô phỏng sang step tiếp theo
        self.current_step += 1
        self.hosts = update_hosts_from_df(self.df, step=self.current_step)

        # 3. Tính reward: giảm variance tải host
        prev_loads = np.array([h.host_cpu_usage for h in self.hosts.values()])
        reward = -np.var(prev_loads)  # muốn giảm variance

        done = self.current_step >= self.df["timestamp"].nunique() - 1
        return self._get_state(), reward, done, {}
    def _get_state(self):
        state = []
        for h in self.hosts.values():
            state.append(h.host_cpu_usage)
            state.append(len(h.vms))
        return np.array(state, dtype=np.float32)

    def _migrate_top_vm(self, host):
        if not host.vms:
            return
        top_vm = max(host.vms, key=lambda vm: vm.cpu_usage)
        target_host = self._find_best_host(exclude=host.hostname)
        if target_host:
            migrate_vm(top_vm.uuid, host, target_host)

    def _find_best_host(self, exclude=None):
        candidates = [h for h in self.hosts.values() if h.hostname != exclude]
        if not candidates:
            return None
        return min(candidates, key=lambda h: h.host_cpu_usage)
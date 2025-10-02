import simpy
import threading
from data.utils import load_data
from simulation.env import simulation_process
from simulation.libs import Logger
from simulation import state
import uvicorn

def run_simulation():
    csv_path = "/home/thuong/data/merged_output/test_simulate.csv"
    df = load_data(csv_path)
    Logger.info("[SIMULATION] START SIMULATION")
    env = simpy.Environment()
    # chạy process của bạn
    env.process(simulation_process(env, df))
    env.run(until=5)
    print("=== Hosts after simulation ===")
    print(state.hosts.keys())
    
    # print("\n=== FINAL STATE ===")
    # for hn, h in state.hosts.items():
    #     print(f"Host {hn} | CPU={h.host_cpu_usage} | VMs={list(h.uuid_to_vm.keys())}")
    Logger.info("[SIMULATION] END SIMULATION")

def run_api():
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000)

def main():
    
    sim_thread = threading.Thread(target=run_simulation, daemon=True)
    sim_thread.start()
    run_api()   # chạy API trong main thread
    # run_simulation()
if __name__ == "__main__":
    main()
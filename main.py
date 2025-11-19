import simpy
import threading
from data.utils import load_pm_json
from simulation.env import simulation_process_json
from simulation.libs import Logger
import subprocess
import uvicorn
import socket
from pathlib import Path

PORT = 8000
JSON_DIR = Path("data/CSV-FileNew/dataset")
MAX_FILE = 117


def check_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

if check_port_in_use(8000):
    print("Port 8000 đã được dùng. Hãy dừng process cũ trước.")
    exit(1)
    
def kill_port(port):
    subprocess.run(f"lsof -t -i:{port} | xargs -r kill -9", shell=True)
    
def run_simulation_json(n_files: int = 1):
    """
    Chạy simulation JSON trong thread, đọc n_files PM từ JSON_DIR
    """
    pm_list = load_pm_json(JSON_DIR, n_files)  # JSON_DIR là Path, n_files là số file
    env = simpy.Environment()
    env.process(simulation_process_json(env, pm_list))
    env.run()
    Logger.info("[SIM] Simulation finished")
    
def start_simulation_thread_json(n_files: int = 1):
    Logger.info(f"[SIMULATION] START SIMULATION with {n_files} PMs")
    thread = threading.Thread(target=run_simulation_json, 
                              args=(n_files,), 
                              daemon=True)
    thread.start()
    Logger.info("[SIMULATION] Simulation thread started")
    return thread

def main():
    if check_port_in_use(8000):
        print("Port 8000 đang dùng. Dừng process cũ trước.")
        kill_port(8000)
        
    start_simulation_thread_json(n_files=117)
    uvicorn.run("api_server:app", host="0.0.0.0", port=PORT, reload=False)

if __name__ == "__main__":
    main()
    
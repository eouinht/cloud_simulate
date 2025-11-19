import simpy
import threading
from data.utils import load_pm_json
from simulation.env import SimulationEnv
from simulation.libs import Logger
import subprocess
import uvicorn
import socket
from pathlib import Path
import time 

PORT = 8000
JSON_DIR = Path("data/CSV-FileNew/dataset")
MAX_FILE = 117
N_FILE = 50
API = "http://127.0.0.1:8000"

pm_list = load_pm_json(JSON_DIR, N_FILE)

def start_api():
    """Khởi động FastAPI trong thread riêng."""
    Logger.info("[MAIN] Starting API server...")
    uvicorn.run("api_server:app", host="0.0.0.0", port=PORT, reload=False)

def wait_for_port(port=8000, timeout=10):
    """Chờ API server bind xong port trước khi tiếp tục."""
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.1)
    return False

def main():
    Logger.info(f"[MAIN] Loaded {len(pm_list)} PMs from {JSON_DIR}")
    
    # Start API server trong thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # Chờ API server bind xong port
    if not wait_for_port(PORT, timeout=10):
        Logger.error("API server chưa sẵn sàng sau 10s, dừng chương trình.")
        return

    Logger.info("[MAIN] API server ready, starting simulation...")
    
    sim_env = SimulationEnv(pm_list, api_url=API)
    # Start API server (uvicorn) trên main thread
    # uvicorn.run("api_server:app", host="0.0.0.0", port=PORT, reload=False)
    # Start simulation + scheduler
    sim_env.run()
    Logger.info("[MAIN] Simulation finished.")
    
if __name__ == "__main__":
    main()
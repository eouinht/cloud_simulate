# Cloud Simulation with API

Dự án này mô phỏng môi trường Cloud Computing bao gồm Host và VM. Dữ liệu đầu vào lấy từ file CSV thực tế, được xử lý bằng SimPy để mô phỏng theo thời gian. Trạng thái hệ thống (host, VM) được lưu trong `simulation/state.py` và có thể truy vấn thông qua REST API (FastAPI + Uvicorn). 

Mục tiêu của dự án: mô phỏng tài nguyên cloud (CPU của host, usage và network của VM), cung cấp API để quan sát trạng thái hệ thống sau mô phỏng, đồng thời chuẩn bị nền tảng cho nghiên cứu VM migration và load balancing. 

**Yêu cầu:** Python >= 3.11, các thư viện `simpy`, `fastapi`, `uvicorn`, `pandas`, `numpy`.  

**Cấu trúc dự án:**  
- `main.py`: chạy mô phỏng và API server.  
- `api_server.py`: khai báo các endpoint FastAPI.  
- `simulation/`: chứa các module mô phỏng.  
  - `env.py`: hàm mô phỏng, cập nhật trạng thái host và VM.  
  - `host.py`: class Host.  
  - `vm.py`: class VM.  
  - `observe.py`: kiểm tra và in trạng thái host/VM.  
  - `state.py`: global state (`hosts` và `vms`).  
- `data/utils.py`: load và xử lý CSV.  
- `requirements.txt`: danh sách dependencies.  

**Cách chạy:**  
1. Tạo môi trường ảo và cài dependencies:  
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   pip install -r requirements.txt
2. Chạy mô phỏng 
    ```bash
    python3 main.py
**REST API:**

- GET /hosts: trả về danh sách host.
- GET /hosts/{hostname}: trả về thông tin chi tiết host gồm cpu_usage và danh sách VM, mỗi VM có uuid, cpu_usage, cpu_allocated, network_in, network_out.
- Dữ liệu mô phỏng: CSV input chứa thông tin host/VM theo timestamp, 
    + các cột chính: timestamp,  hostname, host_cpu_usage, 
                                                                                    uuid_set, 
                                                                                    vm_cpu_usage, 
                                                                                    vm_cpu_allocated, 
                                                                                    vm_cpu_steal,
                                                                                    vm_network_in, 
                                                                                    vm_network_out.

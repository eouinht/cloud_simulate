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

**Data**    
CSV input chứa thông tin host/VM theo timestamp, hostname, host_cpu_usage, 

**REST API:**

- GET /

Trả về thông báo chào.
- GET /hosts

Lấy danh sách host và load tổng quan:
  ```bash
  {
    "timestamp": 12345,
    "hosts": [
      {
        "hostname": 1,
        "total_memory": 32768,
        "mem_in_used": 12000,
        "num_vms": 12
      }
    ]
  }
  ```

- GET /hosts/{hostname}

Lấy đầy đủ thông tin VM trên host:
  ```bash
    {
      "hostname": 1,
      "cpu_usage": 72.5,
      "num_vms": 10,
      "vms": [
        {
          "uuid": "vm123",
          "cpu_usage": 20.1,
          "vm_cpu_steal": 4.0,
          "cpu_allocated": 1.0,
          "memory": 512,
          "network_in": 20.2,
          "network_out": 15.3,
          "migrated": false,
          "placemented": true
        }
      ]
    }
  ```
- POST /creat_vm

Tạo VM mới:
  ```bash
    #input
    {
      "uuid": "vm001",
      "cpu_allocated": 1.0,
      "cpu_usage": 20.0,
      "vm_cpu_steal": 0.0,
      "net_in": 0,
      "net_out": 0
    }

    #output
    {
      "status": "create new vm is successfully",
      "vm": {
        "uuid": "vm001",
        "cpu_allocated": 1.0,
        "cpu_usage": 20.0,
        "net_in": 0,
        "net_out": 0,
        "host": null
      }
    }

  ```

- POST /hosts/{hostname}/assign-vm    
  
Gán VM vào một host:
  ```bash
    #input
    {
      "uuid": "vm001"
    }

    #output
    {
      "status": "successfully embeded vm001 to host 3",
      "host": 3,
      "vm": "vm001"
    }
  ```
- POST /migrate

Migrate 1 VM giữa các host:
  ```bash
      #input
      {
        "uuid": "vm001",
        "des_host": "4"
      }

      #output
      {
        "message": "VM vm001 migrated from 2 → 4",
        "from": 2,
        "to": 4,
        "timestamp": 123,
        "vm": {
          "uuid": "vm001",
          "host": 4,
          "cpu_usage": 20.0,
          "vm_cpu_steal": 0.0,
          "cpu_allocated": 1.0,
          "network_in": 0,
          "network_out": 0
        }
      }
  ```

- GET /vm/{uuid}/steal_time

Check CPU steal time của VM.

**API DÀNH CHO SCHEDULER**

Quan sát hệ thống:
  - GET /hosts
  - GET /hosts/{hostname}
  
Tạo mới:
  - POST /creat_vm
  - POST /hosts/{hostname}/assign-vm

Điều khiển tài nguyên (migrate):
  - POST /migrate

Thông số nâng cao:
  - GET /vm/{uuid}/steal_time

                                                                                    

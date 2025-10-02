import os
from tabulate import tabulate
from colorama import Fore, Style
import re
from datetime import datetime
RESET_TEXT = '\x1b[0m'
BOLD_TEXT = '\x1b[1m'

INFO_TEXT = '\x1b[34m'
WARNING_TEXT = '\x1b[33m'
ERROR_TEXT = '\x1b[31m'
CRITICAL_TEXT = '\x1b[35m'
SUCCEED_TEXT = '\x1b[32m'


class Const:
    total_day = 14

    APP_MEMORY_FOLDER = "./data/app_memory"
    INVOCATIONS_FOLDER = "./data/invocations"
    DURATIONS_FOLDER = "./data/function_durations"


def getFile(folder: str):
    files = [f for f in os.listdir(
        folder) if os.path.isfile(os.path.join(folder, f)) and f != '.gitkeep']

    return files

class Logger:
    @staticmethod
    def _timestamp():
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    @staticmethod
    def info(text):
        print(f'{Logger._timestamp()} {INFO_TEXT}- [INFO] {text}{RESET_TEXT}')

    @staticmethod
    def warning(text):
        print(f'{Logger._timestamp()} {WARNING_TEXT}- [WARN] {text}{RESET_TEXT}')

    @staticmethod
    def error(text):
        print(f'{Logger._timestamp()} {ERROR_TEXT}- [ERRO] {text}{RESET_TEXT}')

    @staticmethod
    def critical(text):
        print(f'{Logger._timestamp()} {CRITICAL_TEXT}- [CRIT] {text}{RESET_TEXT}')

    @staticmethod
    def succeed(text):
        print(f'{Logger._timestamp()} {SUCCEED_TEXT}- [SUCC] {text}{RESET_TEXT}')

    @staticmethod
    def normal(text):
        print(f'{Logger._timestamp()} {text}')
    
    @staticmethod
    def show_hosts_summary(hosts, highlight_threadhold=80.00):
        """ Hien thi bang tong quan cac host.
        Highlight host co CPU usage tren highlight_threadhold
        """  
        data = []  
        for i, h in enumerate(hosts.values()): #host la dict
            cpu_val = h.host_cpu_usage
            cpu_str = f"{cpu_val:.2f}%"
            if cpu_val >= highlight_threadhold:
                cpu_str = Fore.RED + cpu_str + Style.RESET_ALL
            data.append([i, h.hostname, cpu_str, len(h.vms)])

        table = tabulate(data,
                         headers=["Index",
                                  "Hostname",
                                  "CPU Usage",
                                  "VMs"],
                         tablefmt="fancy_grid")
        # Tô màu xanh dương cho toàn bộ viền bảng
        table_colored = re.sub(r"([╒╞╪╡╤╧╘╛╒╕╤╞╪╡╘╛╧╤╪╞╤╕│─═])",
                            lambda m: Fore.BLUE + m.group(1) + Style.RESET_ALL,
                            table)

        print("\n" + table_colored)
    @staticmethod
    def show_vms_in_host(vms, highlight_threadhold=30.0):    
        """ Hiẻn thị bảng thong tin các VM trong host."""
        data = []
        for vm in vms:
            cpu_val = vm.cpu_usage
            cpu_str = f"{cpu_val:.2f}%"
            if cpu_val >= highlight_threadhold:
                cpu_str = Fore.RED + cpu_str + Style.RESET_ALL
            data.append([vm.uuid, cpu_str, f"{vm.cpu_allocated:.2f}%", f"{vm.vm_cpu_steal:.2f}%"])
            
            table = tabulate(data,
                             headers=["UUID",
                                      "CPU Usage",
                                      "CPU Allocated",
                                      "CPU Steal"],
                             tablefmt="fancy_grid")
            # Tô màu xanh dương cho toàn bộ viền bảng
            table_colored = re.sub(r"([╒╞╪╡╤╧╘╛╒╕╤╞╪╡╘╛╧╤╪╞╤╕│─═])",
                                lambda m: Fore.BLUE + m.group(1) + Style.RESET_ALL,
                                table)
        print ("\n" + table_colored)
    
        

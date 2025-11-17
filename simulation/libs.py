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
    LOG_FOLDER = "./logs"
    LOG_FILE_NAME = "simulation.log"
    PRINT_TO_SCREEN = False
    
    @staticmethod
    def _ensure_log_folder():
        if not os.path.exists(Logger.LOG_FOLDER):
            os.makedirs(Logger.LOG_FOLDER)
    
    @staticmethod
    def _log_file_path():
        Logger._ensure_log_folder()
        return os.path.join(Logger.LOG_FOLDER, Logger.LOG_FILE_NAME)

    @staticmethod
    def _timestamp():
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    @staticmethod
    def _write_to_file(text):
        path = Logger._log_file_path()
        with open(Logger._log_file_path(), "a") as f:
            f.write(text + "\n")
            
    @staticmethod
    def info(text):
        log_text = f"{Logger._timestamp()} [INFO] {text}"
        if Logger.PRINT_TO_SCREEN:
            print(log_text)
        Logger._write_to_file(log_text)

    @staticmethod
    def warning(text):
        log_text = f"{Logger._timestamp()} [WARN] {text}"
        if Logger.PRINT_TO_SCREEN:
            print(log_text)
        Logger._write_to_file(log_text)

    @staticmethod
    def error(text):
        log_text = f"{Logger._timestamp()} [ERRO] {text}"
        if Logger.PRINT_TO_SCREEN:
            print(log_text)
        Logger._write_to_file(log_text)

    @staticmethod
    def succeed(text):
        log_text = f"{Logger._timestamp()} [SUCC] {text}"
        if Logger.PRINT_TO_SCREEN:
            print(log_text)
        Logger._write_to_file(log_text)

    @staticmethod
    def normal(text):
        log_text = f"{Logger._timestamp()} {text}"
        if Logger.PRINT_TO_SCREEN:
            print(log_text)
        Logger._write_to_file(log_text)
    @staticmethod
    def show_hosts_summary(hosts, highlight_threadhold=80.00):
        """ Hien thi bang tong quan cac host.
        Highlight host co CPU usage tren highlight_threadhold
        """  
        data = []  
        for i, h in enumerate(hosts.values()): #host la dict
            cpu_val = h.cpu_usage
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
            data.append([vm.uuid, cpu_str, f"{vm.cpu_allocated:.2f}", f"{vm.vm_cpu_steal:.2f}%"])
            
            table = tabulate(data,
                             headers=["UUID",
                                      "CPU Usage",
                                      "CPU Allocated (core)",
                                      "CPU Steal"],
                             tablefmt="fancy_grid")
            # Tô màu xanh dương cho toàn bộ viền bảng
            table_colored = re.sub(r"([╒╞╪╡╤╧╘╛╒╕╤╞╪╡╘╛╧╤╪╞╤╕│─═])",
                                lambda m: Fore.BLUE + m.group(1) + Style.RESET_ALL,
                                table)
        print ("\n" + table_colored)
    
        

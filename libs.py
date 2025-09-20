import os
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
    def info(text):
        print(f'{INFO_TEXT}{"- [INFO] "}{text}{RESET_TEXT}')

    @staticmethod
    def warning(text):
        print(
            f'{WARNING_TEXT}{"- [WARN] "}{text}{RESET_TEXT}')

    @staticmethod
    def error(text):
        print(f'{ERROR_TEXT}{"- [ERRO] "}{text}{RESET_TEXT}')

    @staticmethod
    def critical(text):
        print(
            f'{CRITICAL_TEXT}{"- [CRIT] "}{text}{RESET_TEXT}')

    @staticmethod
    def succeed(text):
        print(
            f'{SUCCEED_TEXT}{"- [SUCC] "}{text}{RESET_TEXT}')

    @staticmethod
    def normal(text):
        print(text)
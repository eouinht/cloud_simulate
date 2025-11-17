import pandas as pd
import os
from simulation.libs import Logger
import numpy as np
import ast
import re
def load_data(csv_path:str):
    """
        Ham doc du lieu tu file CSV va tra ve pandas Dataframe
    """

    if not os.path.exists(csv_path):
        Logger.error(f"Khong tim that file: {csv_path}")
        return None
    
    try:
        Logger.info(f"Dang doc du lieu tu file: {csv_path}")
        df = pd.read_csv(csv_path)
        Logger.succeed(f"Doc thanh cong file: {csv_path}")
        return df
    
    except Exception as e:
        Logger.error(f"Loi khi doc file: {e}")
        return None       

def safe_list_parse(value):
    """Chuyển chuỗi list thành list an toàn, nếu lỗi thì trả về list rỗng."""
    if isinstance(value, list):
        return value
    if value is None or value == "" or str(value).lower() == "nan":
        return []
    try:
        # chuẩn hóa chuỗi trước khi eval
        val = str(value).replace("nan", "0").replace("NaN", "0")
        return ast.literal_eval(val)
    except Exception as e:
        Logger.error("Parse error:", value, e)  # debug
        return []

def safe_float(x):
    """Chuyển về float, thay NaN hoặc lỗi thành 0."""
    try:
        val = float(x)
        if np.isnan(val):
            return 0.0
        return val
    except Exception:
        return 0.0

def parse_set_string(s):
    if not isinstance(s,str):
        return []
    
    s = s.strip().strip("{}")
    if not s:
        return []
    
    s = re.sub(f"[\[\]]", "", s)
    parts = [x.strip() for x in s.split(",") if x.strip]
    
    result = []
    for x in parts:
        try:
            result.append(float(x))
        except ValueError:
            result.append(x)    
    return result
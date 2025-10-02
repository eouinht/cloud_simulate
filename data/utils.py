import pandas as pd
import os
from sim_thuong.simulation.libs import Logger

def load_data(csv_path:str):
    """
        Ham doc du lieu tu file CSV va tra ve pandas Dataframe
    """
    # df = pd.read_csv(csv_path)
    # df["timestamp"] = pd.to_datetime(df["timestamp"])
    # return df
    if not os.path.exists(csv_path):
        Logger.error(f"Khong tim that file: {csv_path}")
        return None
    
    try:
        Logger.info(f"Dang doc du lieu tu file: {csv_path}")
        df = pd.read_csv(csv_path)
        Logger.succeed(f"Doc thanh cong file: {csv_path}")
        return df
    except Exception as e:
        Logger.critical(f"Loi khi doc file: {e}")
        return None        
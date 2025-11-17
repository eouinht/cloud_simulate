import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # thư mục data_loader.py
# Đường dẫn CSV gốc
CSV_PATH = os.path.join(BASE_DIR,"CSV-FileNew", "vm_offline_schedueling.csv")
# Đường dẫn cache Parquet (không ghi đè CSV)
CACHE_PATH = os.path.join(BASE_DIR,"CSV-FileNew", "vm_offline_schedueling_cache.parquet")

def load_data():
    """
    Load DataFrame từ cache Parquet nếu tồn tại.
    Nếu không, đọc CSV, tạo cache và trả về DataFrame.
    """
    if os.path.exists(CACHE_PATH):
        print("[DataLoader] Loading cached DataFrame...")
        try:
            df = pd.read_parquet(CACHE_PATH, engine='pyarrow')
            print(f"[DataLoader] Loaded cached DataFrame with {len(df)} rows.")
        except Exception as e:
            print(f"[DataLoader] Failed to load cached Parquet: {e}")
            df = None
    else:
        df = None

    if df is None:
        print("[DataLoader] Cache not found or failed to load, reading CSV...")
        try:
            df = pd.read_csv(CSV_PATH)
            print(f"[DataLoader] Loaded CSV with {len(df)} rows.")
            # Lưu cache Parquet
            try:
                df.to_parquet(CACHE_PATH, engine='pyarrow', index=False)
                print(f"[DataLoader] Cached DataFrame to {CACHE_PATH}")
            except Exception as e:
                print(f"[DataLoader] Failed to cache DataFrame: {e}")
        except Exception as e:
            print(f"[DataLoader] Failed to read CSV: {e}")
            df = None

    return df

def load_simulation_data():
    """
    Load DataFrame để chạy simulation.
    Ưu tiên cache Parquet, nếu không tồn tại hoặc load thất bại thì đọc CSV.
    """
    df = None

    if os.path.exists(CACHE_PATH):
        try:
            print(f"[DataLoader] Loading cached DataFrame from {CACHE_PATH} ...")
            df = pd.read_parquet(CACHE_PATH, engine='pyarrow')
            print(f"[DataLoader] Loaded cached DataFrame with {len(df)} rows.")
        except Exception as e:
            print(f"[DataLoader] Failed to load cache: {e}")
            df = None

    if df is None:
        # Load CSV và cache lại
        df = load_data()

    return df
# Nếu chạy trực tiếp, đọc DataFrame
if __name__ == "__main__":
    df = load_data()
    if df is not None:
        print(f"[DataLoader] Data ready with {len(df)} rows.")
    else:
        print("[DataLoader] Data could not be loaded.")

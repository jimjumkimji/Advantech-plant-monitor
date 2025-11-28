# backend/dropbox/service.py  (ZIP-ACCELERATED VERSION)

import io
import tempfile
import zipfile
from typing import List, Dict, Optional, Literal
from datetime import datetime

import dropbox
import pandas as pd
import numpy as np

from backend.dropbox.env import DROPBOX_TOKEN, WISE4051_ROOT, WISE4012_ROOT


# ─────────────────────────────────────────────────────────────
# Sensor Columns
# ─────────────────────────────────────────────────────────────
CO2_COL = "COM_1 Wd_0"
TEMP_COL = "COM_1 Wd_1"
HUMID_COL = "COM_1 Wd_2"

LEAF_COL = "AI_0 Val"
GROUND_COL = "AI_1 Val"


# ─────────────────────────────────────────────────────────────
# CACHE
# ─────────────────────────────────────────────────────────────
_cache: Dict[str, pd.DataFrame] = {}
_sensor_cache = {
    "wise4051": {"data": None, "last_updated": None},
    "wise4012": {"data": None, "last_updated": None},
}


# ─────────────────────────────────────────────────────────────
# Dropbox Utils
# ─────────────────────────────────────────────────────────────
def get_client() -> dropbox.Dropbox:
    return dropbox.Dropbox(DROPBOX_TOKEN)


def list_date_folders(root_path: str) -> List[str]:
    """
    List subfolders (day folders). Works for WISE-4051 and WISE-4012.
    """
    dbx = get_client()
    res = dbx.files_list_folder(root_path)
    folders: List[str] = []

    while True:
        for entry in res.entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                folders.append(entry.path_display)
        if not res.has_more:
            break
        res = dbx.files_list_folder_continue(res.cursor)

    return folders


# ─────────────────────────────────────────────────────────────
# ZIP FAST DOWNLOAD (instead of reading CSV file-by-file)
# ─────────────────────────────────────────────────────────────
def download_folder_as_zip(dbx: dropbox.Dropbox, folder_path: str) -> str:
    """
    Downloads a Dropbox folder as a single ZIP file.
    MUCH faster than downloading each CSV individually.
    """
    print(f"📦 Download ZIP: {folder_path}")
    _, res = dbx.files_download_zip(folder_path)

    temp_zip_path = tempfile.mktemp(suffix=".zip")
    with open(temp_zip_path, "wb") as f:
        f.write(res.content)

    return temp_zip_path


def read_zip_csvs(zip_path: str) -> pd.DataFrame:
    """
    Extract CSVs from ZIP → merge → sort by timestamp.
    """
    dfs = []

    with zipfile.ZipFile(zip_path, "r") as z:
        for f in z.namelist():
            if f.lower().endswith(".csv"):
                with z.open(f) as fp:
                    df = pd.read_csv(fp)
                    df = add_timestamp_column(df)
                    dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df_all = pd.concat(dfs, ignore_index=True)
    df_all = df_all.sort_values("timestamp").reset_index(drop=True)
    return df_all


# ─────────────────────────────────────────────────────────────
# Timestamp Builder
# ─────────────────────────────────────────────────────────────
def add_timestamp_column(df: pd.DataFrame) -> pd.DataFrame:
    if "timestamp" in df.columns:
        return df

    if "TIM" in df.columns:
        df["timestamp"] = pd.to_datetime(df["TIM"], errors="coerce")
        return df

    keys = {
        "year": ["Year", "YEAR", "year"],
        "month": ["Month", "MONTH", "month"],
        "day": ["Day", "DAY", "day"],
        "hour": ["Hour", "HOUR", "hour"],
        "minute": ["Minute", "MINUTE", "minute"],
        "second": ["Second", "SECOND", "second"],
    }

    def pick(names):
        for n in names:
            if n in df.columns:
                return n
        return None

    y = pick(keys["year"])
    m = pick(keys["month"])
    d = pick(keys["day"])
    h = pick(keys["hour"])
    mn = pick(keys["minute"])
    s = pick(keys["second"])

    if all([y, m, d, h, mn, s]):
        df["timestamp"] = pd.to_datetime(
            dict(year=df[y], month=df[m], day=df[d],
                 hour=df[h], minute=df[mn], second=df[s]),
            errors="coerce"
        )
        return df

    if "Time" in df.columns:
        df["timestamp"] = pd.to_datetime(df["Time"], errors="coerce")
        return df

    raise ValueError("Cannot detect timestamp columns.")


# ─────────────────────────────────────────────────────────────
# Read All CSV (ZIP FAST VERSION)
# ─────────────────────────────────────────────────────────────
def read_all_csv_under(
    root_path: str,
    use_cache: bool = True,
    skip_old_data: bool = True,
) -> pd.DataFrame:

    if use_cache and root_path in _cache:
        print(f"✔ Cache used for {root_path}")
        return _cache[root_path]

    dbx = get_client()
    folders = list_date_folders(root_path)
    if skip_old_data and len(folders) > 7:
        folders = sorted(folders)[-7:]   # keep last 7 subfolders

    dfs = []

    for folder in folders:
        try:
            zip_path = download_folder_as_zip(dbx, folder)
            df = read_zip_csvs(zip_path)
            dfs.append(df)
        except Exception as e:
            print(f"⚠️ Failed ZIP load in {folder}: {e}")

    if not dfs:
        return pd.DataFrame()

    df_all = pd.concat(dfs, ignore_index=True)
    df_all = df_all.sort_values("timestamp").reset_index(drop=True)

    if use_cache:
        _cache[root_path] = df_all
        print(f"💾 Cached ({len(df_all)} rows) for {root_path}")

    return df_all


# ─────────────────────────────────────────────────────────────
# Export Cleaner
# ─────────────────────────────────────────────────────────────
def df_to_records(df: pd.DataFrame) -> List[Dict]:
    if df.empty:
        return []
    df = df.replace({np.nan: None})
    return df.to_dict(orient="records")


# ─────────────────────────────────────────────────────────────
# Aggregation
# ─────────────────────────────────────────────────────────────
def aggregate_data(
    df: pd.DataFrame,
    interval: Literal["1min", "5min", "15min", "30min", "1hour"],
) -> pd.DataFrame:

    if df.empty:
        return df

    freq = {
        "1min": "1T",
        "5min": "5T",
        "15min": "15T",
        "30min": "30T",
        "1hour": "1H",
    }.get(interval, "5T")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    df_numeric = df[["timestamp"] + numeric_cols].copy()

    df_agg = df_numeric.set_index("timestamp").resample(freq).mean().reset_index()
    return df_agg


# ─────────────────────────────────────────────────────────────
# Bioelectric Voltage Conversion
# ─────────────────────────────────────────────────────────────
def convert_bioelectric_voltage(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    def adc_to_voltage(v):
        try:
            return (float(v) - 32768.0) * (20.0 / 65535.0)
        except Exception:
            return None

    if LEAF_COL in df.columns:
        df["Leaf_Voltage"] = df[LEAF_COL].apply(adc_to_voltage)
    if GROUND_COL in df.columns:
        df["Ground_Voltage"] = df[GROUND_COL].apply(adc_to_voltage)

    return df


# ─────────────────────────────────────────────────────────────
# High-level API
# ─────────────────────────────────────────────────────────────
def get_co2_all_raw(limit=None, interval="raw") -> List[Dict]:
    df = read_all_csv_under(WISE4051_ROOT)

    if interval != "raw":
        df = aggregate_data(df, interval)

    if limit:
        df = df.tail(limit)

    return df_to_records(df)


def get_elec_all_raw(limit=None, interval="raw") -> List[Dict]:
    df = read_all_csv_under(WISE4012_ROOT)
    df = convert_bioelectric_voltage(df)

    if interval != "raw":
        df = aggregate_data(df, interval)

    if limit:
        df = df.tail(limit)

    return df_to_records(df)


# ─────────────────────────────────────────────────────────────
# REALTIME CACHE
# ─────────────────────────────────────────────────────────────
def refresh_sensor_cache(limit=1000, interval="5min"):
    global _sensor_cache

    print("🔁 Refreshing sensors...")

    # 4051
    df4051 = read_all_csv_under(WISE4051_ROOT, use_cache=False)
    if interval != "raw":
        df4051 = aggregate_data(df4051, interval)
    if limit:
        df4051 = df4051.tail(limit)

    _sensor_cache["wise4051"] = {
        "data": df4051.copy() if not df4051.empty else None,
        "last_updated": datetime.now(),
    }

    # 4012
    df4012 = read_all_csv_under(WISE4012_ROOT, use_cache=False)
    df4012 = convert_bioelectric_voltage(df4012)
    if interval != "raw":
        df4012 = aggregate_data(df4012, interval)
    if limit:
        df4012 = df4012.tail(limit)

    _sensor_cache["wise4012"] = {
        "data": df4012.copy() if not df4012.empty else None,
        "last_updated": datetime.now(),
    }


def get_sensor_cache():
    return _sensor_cache


# ─────────────────────────────────────────────────────────────
# CLEAR CACHE
# ─────────────────────────────────────────────────────────────
def clear_cache():
    global _cache, _sensor_cache
    _cache = {}
    _sensor_cache = {
        "wise4051": {"data": None, "last_updated": None},
        "wise4012": {"data": None, "last_updated": None},
    }
    print("🧹 Cache cleared.")

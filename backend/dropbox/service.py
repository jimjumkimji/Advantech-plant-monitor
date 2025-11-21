import io
from typing import List, Dict

import dropbox
import pandas as pd
import numpy as np  

from backend.dropbox.env import DROPBOX_TOKEN, WISE4051_ROOT, WISE4012_ROOT

CO2_COL = "COM_1 Wd_0"
TEMP_COL = "COM_1 Wd_1"
HUMID_COL = "COM_1 Wd_2"


def get_client() -> dropbox.Dropbox:
    return dropbox.Dropbox(DROPBOX_TOKEN)


def list_date_folders(root_path: str) -> List[str]:
    dbx = get_client()
    res = dbx.files_list_folder(root_path)
    folders: List[str] = []

    while True:
        for entry in res.entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                path = entry.path_lower or entry.path_display
                folders.append(path)
        if not res.has_more:
            break
        res = dbx.files_list_folder_continue(res.cursor)

    return folders


def list_csv_files(dbx: dropbox.Dropbox, folder_path: str) -> List[str]:
    res = dbx.files_list_folder(folder_path)
    files: List[str] = []

    while True:
        for entry in res.entries:
            if isinstance(entry, dropbox.files.FileMetadata) and entry.name.lower().endswith(
                ".csv"
            ):
                path = entry.path_lower or entry.path_display
                files.append(path)
        if not res.has_more:
            break
        res = dbx.files_list_folder_continue(res.cursor)

    return files


def download_csv_to_df(dbx: dropbox.Dropbox, file_path: str) -> pd.DataFrame:
    _, resp = dbx.files_download(file_path)
    content = resp.content.decode("utf-8", errors="ignore")
    df = pd.read_csv(io.StringIO(content))
    return df


def add_timestamp_column(df: pd.DataFrame) -> pd.DataFrame:
    if "timestamp" in df.columns:
        return df

    # เคส WISE-4051: มีคอลัมน์ TIM เป็น ISO time เช่น 2025-11-18T14:44:23+07:00
    if "TIM" in df.columns:
        df["timestamp"] = pd.to_datetime(df["TIM"], errors="coerce")
        if df["timestamp"].isna().all():
            raise ValueError("TIM column exists but cannot parse timestamps")
        return df

    year_cols = ["Year", "YEAR", "year"]
    month_cols = ["Month", "MONTH", "month"]
    day_cols = ["Day", "DAY", "day"]
    hour_cols = ["Hour", "HOUR", "hour"]
    minute_cols = ["Minute", "MINUTE", "minute"]
    second_cols = ["Second", "SECOND", "second"]

    def pick(cols):
        for c in cols:
            if c in df.columns:
                return c
        return None

    y_col = pick(year_cols)
    m_col = pick(month_cols)
    d_col = pick(day_cols)
    h_col = pick(hour_cols)
    mn_col = pick(minute_cols)
    s_col = pick(second_cols)

    if y_col and m_col and d_col and h_col and mn_col and s_col:
        df["timestamp"] = pd.to_datetime(
            dict(
                year=df[y_col],
                month=df[m_col],
                day=df[d_col],
                hour=df[h_col],
                minute=df[mn_col],
                second=df[s_col],
            ),
            errors="coerce",
        )
        return df

    if "Time" in df.columns:
        df["timestamp"] = pd.to_datetime(df["Time"], errors="coerce")
        return df

    raise ValueError("Cannot build timestamp column from CSV (no usable time columns)")


def read_all_csv_under(root_path: str) -> pd.DataFrame:
    dbx = get_client()
    all_rows: List[pd.DataFrame] = []

    folders = list_date_folders(root_path)
    for folder in folders:
        csv_files = list_csv_files(dbx, folder)
        for path in csv_files:
            df = download_csv_to_df(dbx, path)
            df = add_timestamp_column(df)
            all_rows.append(df)

    if not all_rows:
        return pd.DataFrame()

    df_all = pd.concat(all_rows, ignore_index=True)
    df_all = df_all.sort_values("timestamp").reset_index(drop=True)
    return df_all


# ---------- helper: clean NaN ก่อนส่งออก JSON ----------

def df_to_records(df: pd.DataFrame) -> List[Dict]:
    """
    แปลง DataFrame -> list[dict] โดยแปลง NaN เป็น None
    เพื่อให้ JSON encoder ของ FastAPI handle ได้
    """
    if df.empty:
        return []
    df_clean = df.replace({np.nan: None})
    return df_clean.to_dict(orient="records")


# ---------- group functions ----------

def group_hourly(df: pd.DataFrame, value_col: str) -> List[Dict]:
    if df.empty or value_col not in df.columns:
        return []

    grouped = (
        df.groupby(df["timestamp"].dt.floor("h"))[value_col]  # ใช้ 'h' แทน 'H'
        .mean()
        .reset_index()
        .rename(columns={"timestamp": "time", value_col: "value"})
    )
    grouped["time"] = grouped["time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df_to_records(grouped)


def group_daily(df: pd.DataFrame, value_col: str) -> List[Dict]:
    if df.empty or value_col not in df.columns:
        return []

    df["date"] = df["timestamp"].dt.date
    grouped = (
        df.groupby("date")[value_col]
        .mean()
        .reset_index()
        .rename(columns={value_col: "value"})
    )
    grouped["date"] = grouped["date"].astype(str)
    return df_to_records(grouped)


# ---------- CO2 (WISE-4051) ----------

def get_co2_all_raw() -> List[Dict]:
    df = read_all_csv_under(WISE4051_ROOT)
    return df_to_records(df)


def get_co2_all_hourly() -> List[Dict]:
    df = read_all_csv_under(WISE4051_ROOT)
    return group_hourly(df, CO2_COL)


def get_co2_daily() -> List[Dict]:
    df = read_all_csv_under(WISE4051_ROOT)
    return group_daily(df, CO2_COL)


# ---------- Temperature (WISE-4012) ----------

def get_temp_all_raw() -> List[Dict]:
    df = read_all_csv_under(WISE4012_ROOT)
    return df_to_records(df)


def get_temp_all_hourly() -> List[Dict]:
    df = read_all_csv_under(WISE4012_ROOT)
    return group_hourly(df, TEMP_COL)


def get_temp_daily() -> List[Dict]:
    df = read_all_csv_under(WISE4012_ROOT)
    return group_daily(df, TEMP_COL)


# ---------- Humidity (WISE-4012) ----------

def get_humid_all_raw() -> List[Dict]:
    df = read_all_csv_under(WISE4012_ROOT)
    return df_to_records(df)


def get_humid_all_hourly() -> List[Dict]:
    df = read_all_csv_under(WISE4012_ROOT)
    return group_hourly(df, HUMID_COL)


def get_humid_daily() -> List[Dict]:
    df = read_all_csv_under(WISE4012_ROOT)
    return group_daily(df, HUMID_COL)
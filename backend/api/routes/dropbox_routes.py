# app/api/routes/dropbox_routes.py
from fastapi import APIRouter

from backend.dropbox import service as dropbox_service

router = APIRouter(prefix="/dropbox", tags=["dropbox"])


# ---------- CO2 (WISE-4051) ----------

@router.get("/wise4051/co2/all", summary="CO2 raw data (WISE-4051) - all")
def wise4051_co2_all_raw():
    return dropbox_service.get_co2_all_raw()


@router.get("/wise4051/co2/hourly", summary="CO2 hourly average (WISE-4051)")
def wise4051_co2_hourly():
    return dropbox_service.get_co2_all_hourly()


@router.get("/wise4051/co2/daily", summary="CO2 daily average (WISE-4051)")
def wise4051_co2_daily():
    return dropbox_service.get_co2_daily()


# ---------- Temperature (WISE-4051) ----------

@router.get("/wise4012/temp/all", summary="Temperature raw data (WISE-4051) - all")
def wise4012_temp_all_raw():
    return dropbox_service.get_temp_all_raw()


@router.get("/wise4012/temp/hourly", summary="Temperature hourly average (WISE-4051)")
def wise4012_temp_hourly():
    return dropbox_service.get_temp_all_hourly()


@router.get("/wise4012/temp/daily", summary="Temperature daily average (WISE-4051)")
def wise4012_temp_daily():
    return dropbox_service.get_temp_daily()


# ---------- Humidity (WISE-4051) ----------

@router.get("/wise4012/humid/all", summary="Humidity raw data (WISE-4051) - all")
def wise4012_humid_all_raw():
    return dropbox_service.get_humid_all_raw()


@router.get("/wise4012/humid/hourly", summary="Humidity hourly average (WISE-4051)")
def wise4012_humid_hourly():
    return dropbox_service.get_humid_all_hourly()


@router.get("/wise4012/humid/daily", summary="Humidity daily average (WISE-4051)")
def wise4012_humid_daily():
    return dropbox_service.get_humid_daily()
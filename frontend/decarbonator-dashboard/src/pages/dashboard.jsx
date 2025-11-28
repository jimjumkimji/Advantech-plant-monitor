import { useState, useEffect } from "react";
import { getTotalCo2, refreshCo2Cache } from "../utils/co2Cache";

function Dashboard({ sensorData = [], plants = [] }) {
  // For API
  const [totalPlants, setTotalPlants] = useState(0);
  const [totalCo2, setTotalCo2] = useState(0);
  const [bangkokAvgTemp, setBangkokAvgTemp] = useState(null);

  // state สำหรับวันที่/เวลา ที่กำลังเลือก (ยังไม่กด Done)
  const [startDate, setStartDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endDate, setEndDate] = useState("");
  const [endTime, setEndTime] = useState("");

  // state สำหรับช่วงเวลาที่ ยืนยันแล้ว (ตอนกด Done)
  const [appliedRange, setAppliedRange] = useState(null);

  // Sorting state for action logs
  const [sortField, setSortField] = useState("timestamp"); // 'timestamp' | 'plantName' | 'type'
  const [sortDirection, setSortDirection] = useState("desc"); // 'asc' | 'desc'

  useEffect(() => {
    const fetchPlants = async () => {
      try {
        const res = await fetch("/plants/all");
        if (!res.ok) {
          console.error("Failed to fetch plants:", res.status);
          return;
        }
        const data = await res.json();

        if (Array.isArray(data)) {
          setTotalPlants(data.length);
        } else if (Array.isArray(data.plants)) {
          setTotalPlants(data.plants.length);
        } else {
          console.warn("Unknown /plants/all response shape:", data);
        }
      } catch (err) {
        console.error("Error fetching plants:", err);
      }
    };

    const fetchCo2Count = async () => {
      try {
        const totalCo2 = await getTotalCo2();
        setTotalCo2(totalCo2);
      } catch (err) {
        console.error("Error fetching CO2 count:", err);
      }
    };

    const fetchBangkokWeather = async () => {
      try {
        // Kasetsart Bangkhen approx coordinates: lat 13.84725, lon 100.57157
        const url =
          "https://api.open-meteo.com/v1/forecast" +
          "?latitude=13.84725" +
          "&longitude=100.57157" +
          "&daily=temperature_2m_max,temperature_2m_min" +
          "&timezone=Asia%2FBangkok";

        const res = await fetch(url);
        if (!res.ok) {
          console.error("Failed to fetch Bangkok weather:", res.status);
          return;
        }
        const data = await res.json();

        if (
          data.daily &&
          Array.isArray(data.daily.temperature_2m_max) &&
          Array.isArray(data.daily.temperature_2m_min) &&
          data.daily.temperature_2m_max.length > 0 &&
          data.daily.temperature_2m_min.length > 0
        ) {
          const tMax = data.daily.temperature_2m_max[0];
          const tMin = data.daily.temperature_2m_min[0];
          const avg = (tMax + tMin) / 2;
          setBangkokAvgTemp(avg);
        } else {
          console.warn("Unexpected Open-Meteo response shape:", data);
        }
      } catch (err) {
        console.error("Error fetching Bangkok weather:", err);
      }
    };

    fetchPlants();
    fetchCo2Count();
    fetchBangkokWeather();
  }, []);

  // เช็คว่ากรอกครบทั้ง 4 ช่องหรือยัง
  const isComplete =
    startDate && startTime && endDate && endTime;

  // helper แปลง date+time เป็น string ส
  const formatDateTime = (dateStr, timeStr) => {
    if (!dateStr || !timeStr) return "";
    const dt = new Date(`${dateStr}T${timeStr}`);
    return dt.toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  const formatDateTimeDisplay = (date) => {
    if (!date) return "-";
    return date.toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  };

  // -----------------------------
  // Action detection from sensorData
  // sensorData เป็น data ก้อนเดียวกับ graph ใน PlantDetail
  // -----------------------------
  const HUMIDITY_SPIKE = 8; // % ปรับได้
  const LUX_SPIKE_ON = 200; // lux delta up = light on
  const LUX_SPIKE_OFF = 200; // lux delta down = light off

  const renderSortIcon = (field) => {
    if (sortField !== field) return "↕";
    return sortDirection === "asc" ? "↑" : "↓";
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">
          Decarbonator Overview
        </h1>
      {/* Header + KPI row (responsive): title left, KPIs right */}
      <div className="flex flex-col  md:justify-between gap-6 mb-6">
      

        {/* KPI Cards */}
        <div className="w-full md:w-2/3">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-2xl shadow-md px-6 py-4 flex flex-col justify-between">
              <p className="text-xs text-gray-500 mb-2">Total Plant(s):</p>
              {/* <p className="text-2xl font-semibold">{totalPlants}</p> */}
              <p className="text-2xl font-semibold">1</p>
            </div>

            <div className="bg-white rounded-2xl shadow-md px-6 py-4 flex flex-col justify-between">
              <p className="text-xs text-gray-500 mb-2">Bangkok Avg Temp (Today)</p>
              <p className="text-2xl font-semibold">
                {bangkokAvgTemp !== null ? `${bangkokAvgTemp.toFixed(1)} °C` : "-"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default Dashboard;

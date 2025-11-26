import { useState } from "react";

function Dashboard() {
  // For API
  const totalPlants = 2;
  const totalCo2 = 2;

  // state สำหรับวันที่/เวลา ที่กำลังเลือก (ยังไม่กด Done)
  const [startDate, setStartDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endDate, setEndDate] = useState("");
  const [endTime, setEndTime] = useState("");

  // state สำหรับช่วงเวลาที่ "ยืนยันแล้ว" (ตอนกด Done)
  const [appliedRange, setAppliedRange] = useState(null);

  // ใช้เช็คว่ากรอกครบทั้ง 4 ช่องหรือยัง
  const isComplete =
    startDate && startTime && endDate && endTime;

  // helper แปลง date+time เป็นข้อความสวย ๆ
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

  const handleDone = () => {
    if (!isComplete) return;
    setAppliedRange({
      startDate,
      startTime,
      endDate,
      endTime,
    });
  };

  const handleCancel = () => {
    setStartDate("");
    setStartTime("");
    setEndDate("");
    setEndTime("");
    setAppliedRange(null);
  };

  return (
    <div className="p-8 space-y-8">
    {/* หัวข้อใหญ่ + การ์ดสรุป */}
        <h1 className="text-2xl font-bold text-gray-900 mb-1">
        Decarbonator Overview
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl shadow-md px-6 py-4 flex flex-col justify-between">
          <p className="text-xs text-gray-500 mb-2">
            Total Plants
          </p>
          <p className="text-2xl font-semibold">{totalPlants}</p>
        </div>

        <div className="bg-white rounded-2xl shadow-md px-6 py-4 flex flex-col justify-between">
          <p className="text-xs text-gray-500 mb-2">
            Total CO2 Absorbed
          </p>
          <p className="text-2xl font-semibold">
            {totalCo2} ppm
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-md px-6 py-4 flex flex-col justify-between">
          <p className="text-xs text-gray-500 mb-2">?????</p>
          <p className="text-2xl font-semibold">????</p>
        </div>

      </div>

              <hr className="border-t border-gray-300 my-4" />
      {/* ส่วนกราฟ – แสดงเฉพาะเมื่อกด Done แล้ว */}
      {appliedRange && (
        <section className="space-y-4">
          <h2 className="text-m font-medium mb-2">
            <h2 className="text-m font-medium mb-2">
              Comparing data from {formatDateTime(appliedRange.startDate, appliedRange.startTime)} until {formatDateTime(appliedRange.endDate, appliedRange.endTime)}
            </h2>

          </h2>
        </section>
      )}
    </div>
  );
}

export default Dashboard;

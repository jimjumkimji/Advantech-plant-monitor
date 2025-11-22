import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

function PlantDetail({ plant, onBack }) {
  // Sample data - replace with actual API data
  const [sensorData] = useState([
    { timestamp: "2025-11-21T20:00:00+07:00", o2: 20.5, temperature: 25.3, humidity: 65, soilMoisture: 45, light: 320 },
    { timestamp: "2025-11-21T21:00:00+07:00", o2: 21.2, temperature: 24.8, humidity: 67, soilMoisture: 43, light: 280 },
    { timestamp: "2025-11-21T22:00:00+07:00", o2: 20.8, temperature: 24.5, humidity: 68, soilMoisture: 42, light: 150 },
    { timestamp: "2025-11-21T23:00:00+07:00", o2: 21.5, temperature: 24.2, humidity: 70, soilMoisture: 41, light: 50 },
    { timestamp: "2025-11-21T23:37:04+07:00", o2: 21.0, temperature: 24.0, humidity: 71, soilMoisture: 40, light: 20 },
  ]);

  // State for filters
  const [selectedMetric, setSelectedMetric] = useState("o2");
  const [timeRange, setTimeRange] = useState("all");

  const metrics = [
    { value: "o2", label: "O2 Level (%)", color: "#22c55e" },
    { value: "temperature", label: "Temperature (°C)", color: "#ef4444" },
    { value: "humidity", label: "Humidity (%)", color: "#3b82f6" },
    { value: "soilMoisture", label: "Soil Moisture (%)", color: "#a855f7" },
    { value: "light", label: "Light (lux)", color: "#f59e0b" },
  ];

  // Format timestamp for display
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  // Filter data by time range
  const filterDataByTime = (data) => {
    if (timeRange === "all") return data;
    
    const now = new Date();
    const filtered = data.filter(item => {
      const itemDate = new Date(item.timestamp);
      const hoursDiff = (now - itemDate) / (1000 * 60 * 60);
      
      if (timeRange === "1h") return hoursDiff <= 1;
      if (timeRange === "6h") return hoursDiff <= 6;
      if (timeRange === "24h") return hoursDiff <= 24;
      return true;
    });
    
    return filtered.length > 0 ? filtered : data;
  };

  // Format data for chart
  const currentMetric = metrics.find(m => m.value === selectedMetric);
  const filteredData = filterDataByTime(sensorData);
  
  const chartData = filteredData.map(item => ({
    time: formatTime(item.timestamp),
    value: item[selectedMetric],
    fullTimestamp: item.timestamp
  }));

  // Get latest value
  const latestData = sensorData[sensorData.length - 1];

  return (
    <div className="max-w-6xl">
      <button 
        onClick={onBack}
        className="mb-6 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
      >
        ← Back to Plants
      </button>
      
      <div className="bg-white rounded-lg shadow-lg p-8">
        {/* Top Section */}
        <div className="grid grid-cols-2 gap-8 mb-8">
          {/* Left Column - Image and Info */}
          <div>
            <h1 className="text-3xl font-bold mb-2">{plant.name}</h1>
            <p className="text-gray-600 italic mb-6">{plant.species}</p>
            
            <img 
              src={plant.image} 
              alt={plant.name}
              className="w-64 h-64 object-contain mx-auto mb-4"
            />
          </div>

          {/* Right Column - Stats */}
          <div className="space-y-3">
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
              <p className="font-semibold text-blue-900">Plant Information</p>
              <p className="text-sm text-blue-700">Static and real-time data</p>
            </div>

            <div>
              <p className="text-gray-700"><span className="font-semibold">Age:</span> 6 months</p>
              <p className="text-gray-700"><span className="font-semibold">Health:</span> {plant.health}</p>
              <p className="text-gray-700"><span className="font-semibold">Last Watered:</span> {plant.water}</p>
            </div>

            <div className="mt-6 pt-6 border-t">
              <p className="text-gray-700 font-semibold mb-3">(Latest sensor readings)</p>
              <p className="text-gray-700"><span className="font-semibold">O2 Level:</span> {latestData.o2}%</p>
              <p className="text-gray-700"><span className="font-semibold">Temperature:</span> {latestData.temperature}°C</p>
              <p className="text-gray-700"><span className="font-semibold">Humidity:</span> {latestData.humidity}%</p>
              <p className="text-gray-700"><span className="font-semibold">Soil Moisture:</span> {latestData.soilMoisture}%</p>
              <p className="text-gray-700"><span className="font-semibold">Light:</span> {latestData.light} lux</p>
            </div>
          </div>
        </div>

        {/* Graph Section */}
        <div className="border-t pt-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Sensor Data Over Time</h2>
            
            {/* Controls */}
            <div className="flex gap-4">
              {/* Metric Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Metric
                </label>
                <select
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  {metrics.map(metric => (
                    <option key={metric.value} value={metric.value}>
                      {metric.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Time Range Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Time Range
                </label>
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="1h">Last 1 Hour</option>
                  <option value="6h">Last 6 Hours</option>
                  <option value="24h">Last 24 Hours</option>
                  <option value="all">All Data</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="mb-6">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  label={{ value: 'Time', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  label={{ value: currentMetric.label, angle: -90, position: 'insideLeft' }}
                  domain={['auto', 'auto']}
                />
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="bg-white p-3 border border-gray-300 rounded shadow">
                          <p className="text-sm">{payload[0].payload.fullTimestamp}</p>
                          <p className="text-sm font-semibold" style={{ color: currentMetric.color }}>
                            {currentMetric.label}: {payload[0].value}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  name={currentMetric.label}
                  stroke={currentMetric.color}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Current</p>
              <p className="text-2xl font-bold text-gray-900">
                {chartData[chartData.length - 1]?.value}
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Average</p>
              <p className="text-2xl font-bold text-gray-900">
                {(chartData.reduce((sum, d) => sum + d.value, 0) / chartData.length).toFixed(1)}
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Min</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.min(...chartData.map(d => d.value)).toFixed(1)}
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Max</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.max(...chartData.map(d => d.value)).toFixed(1)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PlantDetail;
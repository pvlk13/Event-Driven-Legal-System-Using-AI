import React, { useState } from 'react';
import { Search, AlertCircle, User, Car } from 'lucide-react';
import 'react-tooltip/dist/react-tooltip.css';

const API_ENDPOINT = 'https://3yztciu8dh.execute-api.us-east-1.amazonaws.com';

const SEVERITY_COLOR = {
  point_of_impact: '#e74c3c',
  most_damage: '#e67e22',
  other_damage: '#f1c40f',
  none: '#ecf0f1'
};

const normalizePart = (part) => {
  if (!part) return [];

  const p = part.toUpperCase();

  if (p.includes('FRONT') || p.includes('CENTER FRONT')) return ['FRONT_BUMPER', 'HOOD'];
  if (p.includes('HOOD')) return ['HOOD'];
  if (p.includes('LEFT')) return ['LEFT_DOOR'];
  if (p.includes('RIGHT')) return ['RIGHT_DOOR'];
  if (p.includes('REAR') || p.includes('TRUNK') || p.includes('CENTER REAR')) return ['REAR_BUMPER', 'TRUNK'];
  if (p.includes('SIDE') || p.includes('DOOR')) return ['LEFT_DOOR', 'RIGHT_DOOR'];

  return [];
};

// Determine color for a specific part based on vehicle damage
const getDamageColor = (vehicle, part) => {
  if (!vehicle.damage_locations) return SEVERITY_COLOR.none;

  let highestSeverity = 0;
  let color = SEVERITY_COLOR.none;

  vehicle.damage_locations.forEach((damage) => {
    const parts = normalizePart(damage.part);

    if (parts.includes(part)) {
      const severityValue =
        damage.damage_type === 'point_of_impact' ? 3 :
        damage.damage_type === 'most_damage' ? 2 :
        damage.damage_type === 'other_damage' ? 1 : 0;

      if (severityValue > highestSeverity) {
        highestSeverity = severityValue;
        color =
          damage.damage_type === 'point_of_impact' ? SEVERITY_COLOR.point_of_impact :
          damage.damage_type === 'most_damage' ? SEVERITY_COLOR.most_damage :
          damage.damage_type === 'other_damage' ? SEVERITY_COLOR.other_damage :
          SEVERITY_COLOR.none;
      }
    }
  });

  return color;
};

// Updated placeholder for vehicles, pedestrians, or generic users
const getPlaceholderImage = (type) => {
  const colors = {
    client: 'bg-blue-200',
    opposing: 'bg-orange-200',
    clientVehicle: 'bg-blue-100',
    opposingVehicle: 'bg-orange-100',
    pedestrian: 'bg-green-100', // pedestrian / bicyclist
  };

  return (
    <div className={`w-full h-48 ${colors[type] || 'bg-gray-200'} flex items-center justify-center rounded-lg border-2 border-gray-300`}>
      <div className="text-center">
        {type === 'pedestrian' ? (
          // Show a person icon or a simple SVG figure
          <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto mb-2" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" width={64} height={64}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 12c2.21 0 4-1.79 4-4S14.21 4 12 4 8 5.79 8 8s1.79 4 4 4zM4 20c0-4 8-4 8-4s8 0 8 4v0H4z" />
          </svg>
        ) : type.includes('Vehicle') ? (
          <Car size={64} className="mx-auto text-gray-500 mb-2" />
        ) : (
          <User size={64} className="mx-auto text-gray-500 mb-2" />
        )}
      </div>
    </div>
  );
};

const VehicleDamageVisualizer = ({ vehicle = {}, vehicleLabel = 'Vehicle', vehicleDescription = '' }) => {
  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200">
      <h3 className="text-lg font-bold mb-4 text-center">{vehicleLabel}</h3>

      {vehicleDescription && (
        <p className="text-sm text-gray-600 italic mb-6 text-center">{vehicleDescription}</p>
      )}

      {/* Vehicle Grid */}
      <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(3, 1fr)', width: '100%', maxWidth: '300px', margin: '0 auto' }}>
        {/* Front */}
        <div className="col-start-2 col-end-3">
          <button className="w-full p-4 border-2 border-gray-400 rounded-lg font-bold" style={{ backgroundColor: getDamageColor(vehicle, 'FRONT_BUMPER') }}>Front</button>
        </div>

        {/* Hood */}
        <div className="col-start-2 col-end-3">
          <button className="w-full p-4 border-2 border-gray-400 rounded-lg font-bold" style={{ backgroundColor: getDamageColor(vehicle, 'HOOD') }}>Hood</button>
        </div>

        {/* Left Door */}
        <div>
          <button className="w-full p-6 border-2 border-gray-400 rounded-lg font-bold" style={{ backgroundColor: getDamageColor(vehicle, 'LEFT_DOOR') }}>Left</button>
        </div>

        {/* Cabin */}
        <div>
          <button className="w-full p-6 border-2 border-gray-400 rounded-lg font-bold" style={{ backgroundColor: getDamageColor(vehicle, 'CABIN') }}>Cabin</button>
        </div>

        {/* Right Door */}
        <div>
          <button className="w-full p-6 border-2 border-gray-400 rounded-lg font-bold" style={{ backgroundColor: getDamageColor(vehicle, 'RIGHT_DOOR') }}>Right</button>
        </div>

        {/* Trunk */}
        <div className="col-start-2 col-end-3">
          <button className="w-full p-4 border-2 border-gray-400 rounded-lg font-bold" style={{ backgroundColor: getDamageColor(vehicle, 'TRUNK') }}>Trunk</button>
        </div>

        {/* Rear */}
        <div className="col-start-1 col-end-4">
          <div className="flex items-center justify-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gray-600 border-2 border-gray-800 flex items-center justify-center">
              <div className="w-6 h-6 rounded-full bg-black"></div>
            </div>
            <button className="flex-1 p-4 border-2 border-gray-400 rounded-lg font-bold" style={{ backgroundColor: getDamageColor(vehicle, 'REAR_BUMPER') }}>Rear</button>
            <div className="w-12 h-12 rounded-full bg-gray-600 border-2 border-gray-800 flex items-center justify-center">
              <div className="w-6 h-6 rounded-full bg-black"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const CaseDashboard = () => {
  const [jobId, setJobId] = useState('');
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchCase = async (e) => {
    e.preventDefault();
    if (!jobId.trim()) {
      setError('Please enter a Job ID');
      return;
    }

    setLoading(true);
    setError('');
    setCaseData(null);

    try {
      const response = await fetch(`${API_ENDPOINT}/cases/${jobId}`);
      if (!response.ok) throw new Error(`Case not found (${response.status})`);
      const data = await response.json();
      setCaseData(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch case data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8">
        <h1 className="text-4xl font-bold mb-2">⚖️ Legal Case Dashboard</h1>
        <p className="text-blue-100">Search and view accident case details</p>
      </div>

      {/* Search Section */}
      <div className="max-w-7xl mx-auto p-8">
        <form onSubmit={fetchCase} className="mb-8">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Enter Job ID"
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button type="submit" disabled={loading} className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400">
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {caseData && (
          <div className="space-y-6">
            {/* Client & Opposing Party with Images */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* CLIENT */}
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <h2 className="text-xl font-bold mb-4">👤 Client</h2>
                <div className="mb-4">
                  {(caseData.client_type === 'PEDESTRIAN' || caseData.client_type === 'BICYCLIST') ? (
                    getPlaceholderImage('pedestrian')
                  ) : (
                    caseData.vehicles && caseData.vehicles[0] &&
                    <VehicleDamageVisualizer 
                      vehicle={caseData.vehicles[0]}
                      vehicleLabel={`Client Vehicle - ${caseData.vehicles[0].license_plate || 'N/A'}`}
                      vehicleDescription={caseData.client_vehicle_description}
                    />
                  )}
                  {caseData.client_description && <p className="mt-2 text-sm text-gray-600 italic">{caseData.client_description}</p>}
                </div>
                <p className="mb-2"><strong>Name:</strong> {caseData.client_first_name} {caseData.client_last_name}</p>
                <p className="mb-2"><strong>Type:</strong> <span className="text-blue-600 font-semibold">{caseData.client_type}</span></p>
                <p className="mb-2"><strong>DOB:</strong> {caseData.client_dob}</p>
                <p><strong>Address:</strong> {caseData.client_address}</p>
              </div>

              {/* OPPOSING PARTY */}
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <h2 className="text-xl font-bold mb-4">👤 Opposing Party</h2>
                <div className="mb-4">
                  {caseData.opposing_type === 'PEDESTRIAN' || caseData.opposing_type === 'BICYCLIST' ? (
                    getPlaceholderImage('pedestrian')
                  ) : (
                    caseData.vehicles && caseData.vehicles[1] &&
                    <VehicleDamageVisualizer 
                      vehicle={caseData.vehicles[1]}
                      vehicleLabel={`Opposing Vehicle - ${caseData.vehicles[1].license_plate || 'N/A'}`}
                      vehicleDescription={caseData.opposing_vehicle_description}
                    />
                  )}
                  {caseData.opposing_party_description && <p className="mt-2 text-sm text-gray-600 italic">{caseData.opposing_party_description}</p>}
                </div>
                <p className="mb-2"><strong>Name:</strong> {caseData.opposing_first_name} {caseData.opposing_last_name}</p>
                <p className="mb-2"><strong>Type:</strong> <span className="text-orange-600 font-semibold">{caseData.opposing_type}</span></p>
                <p className="mb-2"><strong>DOB:</strong> {caseData.opposing_dob}</p>
                <p><strong>Address:</strong> {caseData.opposing_address}</p>
              </div>
            </div>

            {/* Remaining sections like accident details, injuries, police report, summary remain unchanged */}
            {/* ... */}
          </div>
        )}
      </div>
    </div>
  );
};

export default CaseDashboard;
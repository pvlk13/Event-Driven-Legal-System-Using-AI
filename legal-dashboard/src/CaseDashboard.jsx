import React, { useState } from 'react';
import { Search, AlertCircle, User, Car, Bike } from 'lucide-react';
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

  const p = String(part).toUpperCase();

  if (p.includes('FRONT') || p.includes('CENTER FRONT')) return ['FRONT_BUMPER', 'HOOD'];
  if (p.includes('HOOD')) return ['HOOD'];
  if (p.includes('LEFT')) return ['LEFT_DOOR'];
  if (p.includes('RIGHT')) return ['RIGHT_DOOR'];
  if (p.includes('REAR') || p.includes('TRUNK') || p.includes('CENTER REAR')) return ['REAR_BUMPER', 'TRUNK'];
  if (p.includes('SIDE') || p.includes('DOOR')) return ['LEFT_DOOR', 'RIGHT_DOOR'];

  return [];
};

const getDamageColor = (vehicle, part) => {
  if (!vehicle?.damage_locations) return SEVERITY_COLOR.none;

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

const normalizeType = (value) => (value || '').toString().trim().toUpperCase();

const isHumanType = (value) => {
  const t = normalizeType(value);
  return t.includes('BICYCL') || t.includes('BICYCLE') || t.includes('PEDESTRIAN');
};

const isBicycleLikeVehicle = (vehicle = {}) => {
  const text = `
    ${vehicle.make || ''}
    ${vehicle.model || ''}
    ${vehicle.owner || ''}
    ${vehicle.license_plate || ''}
    ${vehicle.year || ''}
    ${vehicle.color || ''}
  `.toUpperCase();

  return text.includes('BICYCLE') || text.includes('BIKE');
};

const getMotorVehicles = (vehicles = []) => vehicles.filter((v) => v && !isBicycleLikeVehicle(v));

const HumanPartyCard = ({ type, description }) => {
  const t = normalizeType(type);
  const isBicyclist = t.includes('BICYCL');

  return (
    <div className="w-full h-64 bg-green-50 rounded-lg border-2 border-green-200 flex items-center justify-center">
      <div className="text-center px-4">
        {isBicyclist ? (
          <Bike size={72} className="mx-auto text-green-600 mb-3" />
        ) : (
          <User size={72} className="mx-auto text-green-600 mb-3" />
        )}

        <p className="font-semibold text-green-700">{type || 'PEDESTRIAN'}</p>
        <p className="text-sm text-gray-600 mt-2">Non-motor vehicle party</p>

        {description && (
          <p className="text-sm text-gray-600 italic mt-3">{description}</p>
        )}
      </div>
    </div>
  );
};

const PersonImageCard = ({ type, description, tone = 'blue' }) => {
  const bg = tone === 'orange' ? 'bg-orange-50 border-orange-200' : 'bg-blue-50 border-blue-200';
  const iconColor = tone === 'orange' ? 'text-orange-600' : 'text-blue-600';
  const t = normalizeType(type);
  const isBicyclist = t.includes('BICYCL');

  return (
    <div className={`w-full h-48 rounded-lg border-2 ${bg} flex items-center justify-center`}>
      <div className="text-center px-4">
        {isBicyclist ? (
          <Bike size={64} className={`mx-auto mb-2 ${iconColor}`} />
        ) : (
          <User size={64} className={`mx-auto mb-2 ${iconColor}`} />
        )}
        <p className={`font-semibold ${iconColor}`}>{type || 'PERSON'}</p>
        {description && (
          <p className="mt-2 text-sm text-gray-600 italic">{description}</p>
        )}
      </div>
    </div>
  );
};

const VehiclePlaceholderCard = ({ tone = 'blue' }) => {
  const bg = tone === 'orange' ? 'bg-orange-100' : 'bg-blue-100';
  const iconColor = tone === 'orange' ? 'text-orange-500' : 'text-blue-500';

  return (
    <div className={`w-full h-48 ${bg} flex items-center justify-center rounded-lg border-2 border-gray-300`}>
      <Car size={64} className={iconColor} />
    </div>
  );
};
const VehicleDamageVisualizer = ({ vehicle = {}, vehicleLabel = 'Vehicle', vehicleDescription = '' }) => {
  const labelText = `${vehicleLabel} ${vehicleDescription} ${vehicle?.make || ''} ${vehicle?.model || ''}`.toLowerCase();

  const isBike = labelText.includes('bicycle') || labelText.includes('bike');
  const isPedestrian = labelText.includes('pedestrian') || labelText.includes('on foot');

  if (isPedestrian || isBike) {
    return (
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-bold mb-4 text-center">{vehicleLabel}</h3>

        {vehicleDescription && (
          <p className="text-sm text-gray-600 italic mb-6 text-center">{vehicleDescription}</p>
        )}

        <div className="w-full h-72 bg-green-50 rounded-lg border-2 border-green-200 flex items-center justify-center">
          <div className="text-center px-4">
            {isBike ? (
              <Bike size={80} className="mx-auto text-green-600 mb-3" />
            ) : (
              <User size={80} className="mx-auto text-green-600 mb-3" />
            )}

            <p className="font-semibold text-green-700">
              {isBike ? 'BICYCLIST' : 'PEDESTRIAN'}
            </p>

            <p className="text-sm text-gray-600 mt-2">
              Non-motor vehicle party
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200">
      <h3 className="text-lg font-bold mb-4 text-center">{vehicleLabel}</h3>

      {vehicleDescription && (
        <p className="text-sm text-gray-600 italic mb-6 text-center">{vehicleDescription}</p>
      )}

      <div
        className="grid gap-2"
        style={{
          gridTemplateColumns: 'repeat(3, 1fr)',
          width: '100%',
          maxWidth: '300px',
          margin: '0 auto'
        }}
      >
        <div className="col-start-2 col-end-3">
          <button
            className="w-full p-4 border-2 border-gray-400 rounded-lg font-bold"
            style={{ backgroundColor: getDamageColor(vehicle, 'FRONT_BUMPER') }}
          >
            Front
          </button>
        </div>

        <div className="col-start-2 col-end-3">
          <button
            className="w-full p-4 border-2 border-gray-400 rounded-lg font-bold"
            style={{ backgroundColor: getDamageColor(vehicle, 'HOOD') }}
          >
            Hood
          </button>
        </div>

        <div>
          <button
            className="w-full p-6 border-2 border-gray-400 rounded-lg font-bold"
            style={{ backgroundColor: getDamageColor(vehicle, 'LEFT_DOOR') }}
          >
            Left
          </button>
        </div>

        <div>
          <button
            className="w-full p-6 border-2 border-gray-400 rounded-lg font-bold"
            style={{ backgroundColor: getDamageColor(vehicle, 'CABIN') }}
          >
            Cabin
          </button>
        </div>

        <div>
          <button
            className="w-full p-6 border-2 border-gray-400 rounded-lg font-bold"
            style={{ backgroundColor: getDamageColor(vehicle, 'RIGHT_DOOR') }}
          >
            Right
          </button>
        </div>

        <div className="col-start-2 col-end-3">
          <button
            className="w-full p-4 border-2 border-gray-400 rounded-lg font-bold"
            style={{ backgroundColor: getDamageColor(vehicle, 'TRUNK') }}
          >
            Trunk
          </button>
        </div>

        <div className="col-start-1 col-end-4">
          <div className="flex items-center justify-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gray-600 border-2 border-gray-800 flex items-center justify-center">
              <div className="w-6 h-6 rounded-full bg-black"></div>
            </div>
            <button
              className="flex-1 p-4 border-2 border-gray-400 rounded-lg font-bold"
              style={{ backgroundColor: getDamageColor(vehicle, 'REAR_BUMPER') }}
            >
              Rear
            </button>
            <div className="w-12 h-12 rounded-full bg-gray-600 border-2 border-gray-800 flex items-center justify-center">
              <div className="w-6 h-6 rounded-full bg-black"></div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t text-center">
        <p className="text-sm text-gray-600">
          {vehicle.year || 'N/A'} {vehicle.make || 'N/A'} {vehicle.model || 'N/A'}
        </p>
        <p className="font-mono font-bold text-lg">{vehicle.license_plate || 'N/A'}</p>
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

      if (!response.ok) {
        throw new Error(`Case not found (${response.status})`);
      }

      const data = await response.json();
      setCaseData(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch case data');
    } finally {
      setLoading(false);
    }
  };

  const clientType = normalizeType(caseData?.client_type);
  const opposingType = normalizeType(caseData?.opposing_type);

  const isClientHuman = isHumanType(clientType);
  const isOpposingHuman = isHumanType(opposingType);

  const motorVehicles = getMotorVehicles(caseData?.vehicles || []);

  const clientVehicle = isClientHuman ? null : motorVehicles[0] || null;
  const opposingVehicle = isClientHuman ? motorVehicles[0] || null : motorVehicles[1] || null;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8">
        <h1 className="text-4xl font-bold mb-2">⚖️ Legal Case Dashboard</h1>
        <p className="text-blue-100">Search and view accident case details</p>
      </div>

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
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
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
            {/* Client & Opposing Party */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* CLIENT */}
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <h2 className="text-xl font-bold mb-4">👤 Client</h2>

                <div className="mb-4">
                  {isClientHuman ? (
                    <PersonImageCard
                      type={caseData.client_type}
                      description={caseData.client_description}
                      tone="blue"
                    />
                  ) : (
                    <VehiclePlaceholderCard tone="blue" />
                  )}
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
                  {isOpposingHuman ? (
                    <PersonImageCard
                      type={caseData.opposing_type}
                      description={caseData.opposing_party_description}
                      tone="orange"
                    />
                  ) : (
                    <VehiclePlaceholderCard tone="orange" />
                  )}
                </div>

                <p className="mb-2"><strong>Name:</strong> {caseData.opposing_first_name} {caseData.opposing_last_name}</p>
                <p className="mb-2"><strong>Type:</strong> <span className="text-orange-600 font-semibold">{caseData.opposing_type}</span></p>
                <p className="mb-2"><strong>DOB:</strong> {caseData.opposing_dob}</p>
                <p><strong>Address:</strong> {caseData.opposing_address}</p>
              </div>
            </div>

            {/* Accident Details */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h2 className="text-xl font-bold mb-4">📍 Accident Details</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-gray-600 text-sm">Date</p>
                  <p className="font-semibold">{caseData.accident_date}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Time</p>
                  <p className="font-semibold">{caseData.accident_time}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Location</p>
                  <p className="font-semibold">{caseData.accident_location}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">SOL Date</p>
                  <p className="font-semibold text-red-600">{caseData.sol_date}</p>
                </div>
              </div>
              <div>
                <p className="text-gray-600 text-sm mb-1">Description</p>
                <p className="text-gray-800">{caseData.accident_description}</p>
              </div>
            </div>

            {/* Vehicle Damage Analysis */}
            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <h2 className="text-2xl font-bold mb-8 text-center">🚗 Vehicle Damage Analysis</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Client side */}
                {isClientHuman ? (
                  <div className="bg-white p-6 rounded-lg border border-gray-200 text-center">
                    <h3 className="text-lg font-bold mb-4">
                      Client - {caseData.client_type || 'Non-Vehicle Party'}
                    </h3>

                    <HumanPartyCard
                      type={caseData.client_type}
                      description={caseData.client_vehicle_description || caseData.client_description}
                    />
                  </div>
                ) : (
                  clientVehicle && (
                    <VehicleDamageVisualizer
                      vehicle={clientVehicle}
                      vehicleLabel={isClientHuman
                          ? `Client - ${caseData.client_type || 'Party'}`
                          : `Client Vehicle - ${clientVehicle.license_plate || 'N/A'}`
                      }
                      vehicleDescription={caseData.client_vehicle_description}
                    />
                  )
                )}

                {/* Opposing side */}
                {opposingVehicle ? (
                  <VehicleDamageVisualizer
                    vehicle={opposingVehicle}
                    vehicleLabel={`Opposing Vehicle - ${opposingVehicle.license_plate || 'N/A'}`}
                    vehicleDescription={caseData.opposing_vehicle_description}
                  />
                ) : (
                  <div className="bg-white p-6 rounded-lg border border-gray-200 text-center">
                    <h3 className="text-lg font-bold mb-4">Opposing Vehicle - N/A</h3>
                    <div className="w-full h-64 bg-gray-50 rounded-lg border-2 border-gray-200 flex items-center justify-center">
                      <div className="text-center px-4">
                        <Car size={72} className="mx-auto text-gray-400 mb-3" />
                        <p className="text-gray-500">No motor vehicle found</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap gap-6 justify-center pt-8 mt-8 border-t">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded" style={{ backgroundColor: '#e74c3c' }}></div>
                  <span className="font-semibold">Point of Impact</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded" style={{ backgroundColor: '#e67e22' }}></div>
                  <span className="font-semibold">Most Damage</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded" style={{ backgroundColor: '#f1c40f' }}></div>
                  <span className="font-semibold">Other Damage</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded" style={{ backgroundColor: '#ecf0f1', border: '2px solid #999' }}></div>
                  <span className="font-semibold">No Damage</span>
                </div>
              </div>
            </div>

            {/* Injuries */}
            {caseData.injured_count > 0 && (
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <h2 className="text-xl font-bold mb-4">🏥 Injuries</h2>
                <p className="mb-2"><strong>Count:</strong> {caseData.injured_count}</p>

                {caseData.injury_types && caseData.injury_types.length > 0 && (
                  <div>
                    <p className="font-semibold mb-2">Types:</p>
                    <div className="flex flex-wrap gap-2">
                      {caseData.injury_types.map((injury, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold"
                        >
                          {injury}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {caseData.injury_treatment && (
                  <p className="mt-2"><strong>Treatment:</strong> {caseData.injury_treatment}</p>
                )}
              </div>
            )}

            {/* Police Report */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h2 className="text-xl font-bold mb-4">📋 Police Report</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-gray-600 text-sm">Report #</p>
                  <p className="font-semibold">{caseData.police_report_number}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Officer</p>
                  <p className="font-semibold">{caseData.officer_name}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Badge</p>
                  <p className="font-semibold">{caseData.badge_number}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Precinct</p>
                  <p className="font-semibold">{caseData.precinct}</p>
                </div>
                <div className="md:col-span-2">
                  <p className="text-gray-600 text-sm">Filed Date</p>
                  <p className="font-semibold">{caseData.filed_date}</p>
                </div>
              </div>
            </div>

            {/* Summary */}
            <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <h2 className="text-xl font-bold mb-2">📝 Summary</h2>
              <p className="text-gray-800">{caseData.summary}</p>
            </div>
          </div>
        )}

        {!caseData && !error && !loading && (
          <div className="text-center py-12 text-gray-500">
            <Search size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-lg">Enter a Job ID to view case details</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CaseDashboard;
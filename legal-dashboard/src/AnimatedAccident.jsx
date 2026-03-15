const AnimatedAccident = ({ vehicles }) => {
  if (!vehicles || vehicles.length < 2) return null;

  const client = vehicles[0];
  const opposing = vehicles[1];

  const getDamageColor = (vehicle, part) => {
    const damage = vehicle.damage_locations?.find(d => d.part?.toUpperCase() === part);
    if (!damage) return '#ecf0f1';
    switch (damage.severity?.toLowerCase()) {
      case 'severe': return '#e74c3c';
      case 'moderate': return '#e67e22';
      case 'minor': return '#f1c40f';
      default: return '#ecf0f1';
    }
  };

  const CarSVG = ({ vehicle, x, y, animateClass }) => (
    <svg className={animateClass} width="120" height="60" viewBox="0 0 120 60" style={{position:'absolute', left:x, top:y}}>
      {/* Car body */}
      <rect x="10" y="10" width="100" height="40" rx="8" fill="#ddd" stroke="#333" strokeWidth="2"/>
      {/* Client damage zones */}
      <rect x="10" y="10" width="30" height="40" fill={getDamageColor(vehicle,'FRONT_BUMPER')} />
      <rect x="40" y="10" width="40" height="40" fill={getDamageColor(vehicle,'CABIN')} />
      <rect x="80" y="10" width="30" height="40" fill={getDamageColor(vehicle,'REAR_BUMPER')} />
      {/* Wheels */}
      <circle cx="20" cy="50" r="5" fill="#222"/>
      <circle cx="100" cy="50" r="5" fill="#222"/>
    </svg>
  );

  return (
    <div className="relative w-full h-64 bg-gray-100 rounded-lg overflow-hidden border border-gray-300">
      {/* Road line */}
      <div className="absolute top-1/2 w-full h-1 bg-yellow-400 transform -translate-y-1/2"></div>

      {/* Client Car */}
      <CarSVG vehicle={client} x={0} y={220} animateClass="animate-clientCar"/>

      {/* Opposing Car */}
      <CarSVG vehicle={opposing} x={600} y={20} animateClass="animate-opposingCar"/>

      {/* Impact flash */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 opacity-0 animate-impactFlash">
        <div className="text-5xl">💥</div>
      </div>
    </div>
  )
}
export default AnimatedAccident
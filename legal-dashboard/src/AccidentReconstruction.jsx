const AccidentReconstruction = ({ vehicles }) => {

  if (!vehicles || vehicles.length < 2) return null;

  const client = vehicles[0];
  const opposing = vehicles[1];

  return (
    <div className="bg-gray-100 p-8 rounded-lg border border-gray-300">
      <h2 className="text-2xl font-bold mb-6 text-center">🚨 Accident Reconstruction</h2>

      <div className="relative w-full h-64 bg-gray-200 overflow-hidden rounded-lg">

        {/* Road Center Line */}
        <div className="absolute top-1/2 left-0 w-full h-1 bg-yellow-400 transform -translate-y-1/2"></div>

        {/* Client Vehicle */}
        <div className="absolute bottom-0 left-0 animate-clientCar">
          <div className="bg-blue-500 text-white px-4 py-2 rounded shadow-lg flex items-center gap-2">
            🚗 {client.make} {client.model}
          </div>
        </div>

        {/* Opposing Vehicle */}
        <div className="absolute top-0 right-0 animate-opposingCar">
          <div className="bg-red-500 text-white px-4 py-2 rounded shadow-lg flex items-center gap-2">
            🚗 {opposing.make} {opposing.model}
          </div>
        </div>

        {/* Impact Flash */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 opacity-0 animate-impactFlash">
          <div className="text-5xl">💥</div>
        </div>

      </div>
    </div>
  )
}
export default AccidentReconstruction
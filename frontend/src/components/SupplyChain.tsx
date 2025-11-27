import { useState, useEffect } from 'react';

interface Asset {
  id: number;
  name: string;
  origin: string;
  current_location: string;
  qr_code?: string;
  notes?: string;
  created_at: string;
}

interface TrackingEvent {
  location: string;
  timestamp: string;
  status: string;
}

export default function SupplyChain() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    origin: '',
    current_location: '',
    notes: '',
  });

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const res = await fetch('http://localhost:8000/supplychain/assets');
      const data = await res.json();
      console.log('Fetched assets:', data);
      setAssets(data);
    } catch (error) {
      console.error('Failed to fetch assets:', error);
    }
  };

  const createAsset = async () => {
    try {
      const res = await fetch('http://localhost:8000/supplychain/assets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (res.ok) {
        setFormData({ name: '', origin: '', current_location: '', notes: '' });
        setShowForm(false);
        fetchAssets();
      }
    } catch (error) {
      console.error('Failed to create asset:', error);
    }
  };

  const getTrackingEvents = (asset: Asset): TrackingEvent[] => {
    return [
      { location: asset.origin, timestamp: asset.created_at, status: 'Origin' },
      { location: asset.current_location, timestamp: new Date().toISOString(), status: 'Current' },
    ];
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Supply Chain Tracking</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          {showForm ? 'Cancel' : 'Track New Product'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Add Product to Track</h2>
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Product Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="p-2 border rounded"
            />
            <input
              type="text"
              placeholder="Origin Location"
              value={formData.origin}
              onChange={(e) => setFormData({ ...formData, origin: e.target.value })}
              className="p-2 border rounded"
            />
            <input
              type="text"
              placeholder="Current Location"
              value={formData.current_location}
              onChange={(e) => setFormData({ ...formData, current_location: e.target.value })}
              className="p-2 border rounded"
            />
            <input
              type="text"
              placeholder="Notes"
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="p-2 border rounded"
            />
          </div>
          <button
            onClick={createAsset}
            className="mt-4 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Add Product
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Tracked Products</h2>
          <div className="space-y-3">
            {assets.map((asset) => (
              <div
                key={asset.id}
                onClick={() => {
                  console.log('Selected asset:', asset);
                  setSelectedAsset(asset);
                }}
                className={`p-4 border rounded-lg cursor-pointer hover:border-green-500 ${
                  selectedAsset?.id === asset.id ? 'border-green-500 bg-green-50' : ''
                }`}
              >
                <h3 className="font-semibold">{asset.name}</h3>
                <p className="text-sm text-gray-600">From: {asset.origin}</p>
                <p className="text-sm text-gray-600">Current: {asset.current_location}</p>
                {asset.notes && (
                  <p className="text-sm text-gray-500 mt-2 italic">Note: {asset.notes}</p>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Tracking Details</h2>
          {selectedAsset ? (
            <div>
              <h3 className="text-lg font-semibold mb-2">{selectedAsset.name}</h3>
              {selectedAsset.qr_code && (
                <div className="mb-4">
                  <img src={selectedAsset.qr_code} alt="QR Code" className="w-32 h-32" />
                </div>
              )}
              <div className="space-y-4">
                {getTrackingEvents(selectedAsset).map((event, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="w-3 h-3 bg-green-600 rounded-full mt-1"></div>
                    <div>
                      <p className="font-semibold">{event.status}</p>
                      <p className="text-sm text-gray-600">{event.location}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(event.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              {selectedAsset.notes && (
                <div className="mt-4 p-3 bg-gray-50 rounded">
                  <p className="text-sm font-semibold text-gray-600 mb-1">Notes:</p>
                  <p className="text-sm text-gray-700">{selectedAsset.notes}</p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-500">Select a product to view tracking details</p>
          )}
        </div>
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { Package, Truck, MapPin, Clock, CheckCircle, AlertCircle, Plane, Ship, Box } from 'lucide-react';
import { secureStorage } from '../lib/security';
import { useTranslation } from '@/i18n/config';

interface Asset {
  id: number;
  name: string;
  origin: string;
  current_location: string;
  qr_code?: string;
  notes?: string;
  created_at: string;
  carrier?: string;
  tracking_number?: string;
  estimated_delivery?: string;
  status?: string;
}

interface TrackingEvent {
  location: string;
  timestamp: string;
  status: string;
  carrier?: string;
  description?: string;
}

const CARRIERS = [
  { id: 'dhl', name: 'DHL Express', icon: '🚚', color: 'bg-red-600' },
  { id: 'fedex', name: 'FedEx', icon: '✈️', color: 'bg-purple-600' },
  { id: 'ups', name: 'UPS', icon: '📦', color: 'bg-yellow-700' },
  { id: 'maersk', name: 'Maersk (Sea)', icon: '🚢', color: 'bg-blue-600' },
  { id: 'local', name: 'Local Delivery', icon: '🛵', color: 'bg-green-600' },
];

const STATUS_ICONS = {
  'Origin': Package,
  'In Transit': Truck,
  'At Hub': Box,
  'Out for Delivery': MapPin,
  'Delivered': CheckCircle,
  'Delayed': AlertCircle,
};

export default function SupplyChain() {
  const { t } = useTranslation();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    origin: '',
    current_location: '',
    notes: '',
    carrier: 'dhl',
    tracking_number: '',
    estimated_delivery: '',
  });

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const token = secureStorage.get<string>('access_token');
      const res = await fetch('/api/supplychain/assets', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          setAssets(data);
        } else {
          console.error('Received non-array data for assets:', data);
          setAssets([]);
        }
      } else {
        console.error('Failed to fetch assets. Status:', res.status);
        setAssets([]);
      }
    } catch (error) {
      console.error('Failed to fetch assets:', error);
      setAssets([]);
    }
  };

  const createAsset = async () => {
    try {
      const token = secureStorage.get<string>('access_token');
      const res = await fetch('/api/supplychain/assets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          ...formData,
          status: 'Origin',
        }),
      });
      if (res.ok) {
        setFormData({
          name: '',
          origin: '',
          current_location: '',
          notes: '',
          carrier: 'dhl',
          tracking_number: '',
          estimated_delivery: '',
        });
        setShowForm(false);
        fetchAssets();
      }
    } catch (error) {
      console.error('Failed to create asset:', error);
    }
  };

  const getTrackingEvents = (asset: Asset): TrackingEvent[] => {
    const events: TrackingEvent[] = [
      {
        location: asset.origin,
        timestamp: asset.created_at,
        status: 'Origin',
        carrier: asset.carrier,
        description: 'Package picked up and processed'
      },
    ];

    if (asset.current_location !== asset.origin) {
      events.push({
        location: 'International Hub',
        timestamp: new Date(new Date(asset.created_at).getTime() + 24 * 60 * 60 * 1000).toISOString(),
        status: 'At Hub',
        carrier: asset.carrier,
        description: 'Arrived at sorting facility'
      });

      events.push({
        location: asset.current_location,
        timestamp: new Date().toISOString(),
        status: 'In Transit',
        carrier: asset.carrier,
        description: 'Out for delivery'
      });
    }

    return events;
  };

  const getCarrierInfo = (carrierId?: string) => {
    return CARRIERS.find(c => c.id === carrierId) || CARRIERS[0];
  };

  const getStatusColor = (status?: string) => {
    const colors: Record<string, string> = {
      'Origin': 'bg-blue-100 text-blue-800',
      'In Transit': 'bg-yellow-100 text-yellow-800',
      'At Hub': 'bg-purple-100 text-purple-800',
      'Out for Delivery': 'bg-orange-100 text-orange-800',
      'Delivered': 'bg-green-100 text-green-800',
      'Delayed': 'bg-red-100 text-red-800',
    };
    return colors[status || 'Origin'] || colors['Origin'];
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">{t('supplyChain.title')}</h1>
          <p className="text-gray-600 mt-2">Product Journey</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 shadow-lg transition-all"
        >
          {showForm ? 'Cancel' : 'Track Product'}
        </button>
      </div>

      {/* Carrier Partners Banner */}
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 mb-8 border border-gray-200">
        <h3 className="text-sm font-semibold text-gray-600 mb-4">TRUSTED LOGISTICS PARTNERS</h3>
        <div className="flex flex-wrap gap-4">
          {CARRIERS.map((carrier) => (
            <div key={carrier.id} className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg shadow-sm">
              <span className="text-2xl">{carrier.icon}</span>
              <span className="font-semibold text-gray-700">{carrier.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Create Shipment Form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-200">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Create New Shipment</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Product Name</label>
              <input
                type="text"
                placeholder="e.g., Organic Rice 50kg"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Logistics Partner</label>
              <select
                value={formData.carrier}
                onChange={(e) => setFormData({ ...formData, carrier: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                {CARRIERS.map((carrier) => (
                  <option key={carrier.id} value={carrier.id}>
                    {carrier.icon} {carrier.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Origin Location</label>
              <input
                type="text"
                placeholder="e.g., Dhaka, Bangladesh"
                value={formData.origin}
                onChange={(e) => setFormData({ ...formData, origin: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Destination</label>
              <input
                type="text"
                placeholder="e.g., New York, USA"
                value={formData.current_location}
                onChange={(e) => setFormData({ ...formData, current_location: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Tracking Number</label>
              <input
                type="text"
                placeholder="e.g., DHL1234567890"
                value={formData.tracking_number}
                onChange={(e) => setFormData({ ...formData, tracking_number: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Estimated Delivery</label>
              <input
                type="date"
                value={formData.estimated_delivery}
                onChange={(e) => setFormData({ ...formData, estimated_delivery: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-gray-700 mb-2">Shipment Notes</label>
              <textarea
                placeholder="Additional information about the shipment..."
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                rows={3}
              />
            </div>
          </div>

          <button
            onClick={createAsset}
            className="mt-6 px-8 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 shadow-lg font-semibold transition-all"
          >
            Create Shipment
          </button>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Active Shipments */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <h2 className="text-2xl font-bold mb-6 text-gray-900 flex items-center gap-2">
            <Package className="w-6 h-6" />
            Active Shipments
          </h2>
          <div className="space-y-4 max-h-[600px] overflow-y-auto">
            {assets.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Package className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>No active shipments</p>
              </div>
            ) : (
              assets.map((asset) => {
                const carrier = getCarrierInfo(asset.carrier);
                return (
                  <div
                    key={asset.id}
                    onClick={() => setSelectedAsset(asset)}
                    className={`p-5 border-2 rounded-xl cursor-pointer transition-all hover:shadow-md ${selectedAsset?.id === asset.id
                        ? 'border-green-500 bg-green-50 shadow-md'
                        : 'border-gray-200 hover:border-green-300'
                      }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="font-bold text-lg text-gray-900">{asset.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`${carrier.color} text-white text-xs px-2 py-1 rounded font-semibold`}>
                            {carrier.icon} {carrier.name}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded font-semibold ${getStatusColor(asset.status)}`}>
                            {asset.status || 'In Transit'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2 text-gray-600">
                        <MapPin className="w-4 h-4" />
                        <span className="font-semibold">From:</span> {asset.origin}
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <MapPin className="w-4 h-4 text-green-600" />
                        <span className="font-semibold">To:</span> {asset.current_location}
                      </div>
                      {asset.tracking_number && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Package className="w-4 h-4" />
                          <span className="font-semibold">Tracking:</span> {asset.tracking_number}
                        </div>
                      )}
                      {asset.estimated_delivery && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Clock className="w-4 h-4" />
                          <span className="font-semibold">ETA:</span> {new Date(asset.estimated_delivery).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Tracking Details */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <h2 className="text-2xl font-bold mb-6 text-gray-900 flex items-center gap-2">
            <Truck className="w-6 h-6" />
            Tracking Details
          </h2>

          {selectedAsset ? (
            <div>
              {/* Shipment Header */}
              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 mb-6 border border-green-200">
                <h3 className="text-xl font-bold text-gray-900 mb-2">{selectedAsset.name}</h3>
                <div className="flex items-center gap-2 mb-3">
                  {(() => {
                    const carrier = getCarrierInfo(selectedAsset.carrier);
                    return (
                      <span className={`${carrier.color} text-white text-sm px-3 py-1 rounded-full font-semibold`}>
                        {carrier.icon} {carrier.name}
                      </span>
                    );
                  })()}
                  <span className={`text-sm px-3 py-1 rounded-full font-semibold ${getStatusColor(selectedAsset.status)}`}>
                    {selectedAsset.status || 'In Transit'}
                  </span>
                </div>
                {selectedAsset.tracking_number && (
                  <p className="text-sm text-gray-700">
                    <span className="font-semibold">Tracking #:</span> {selectedAsset.tracking_number}
                  </p>
                )}
                {selectedAsset.estimated_delivery && (
                  <p className="text-sm text-gray-700 mt-1">
                    <span className="font-semibold">Estimated Delivery:</span>{' '}
                    {new Date(selectedAsset.estimated_delivery).toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                )}
              </div>

              {/* QR Code */}
              {selectedAsset.qr_code && (
                <div className="mb-6 text-center">
                  <img src={selectedAsset.qr_code} alt="QR Code" className="w-40 h-40 mx-auto border-4 border-gray-200 rounded-lg" />
                  <p className="text-xs text-gray-500 mt-2">Scan for instant tracking</p>
                </div>
              )}

              {/* Timeline */}
              <div className="space-y-6">
                <h4 className="font-bold text-gray-900 text-lg mb-4">Shipment Journey</h4>
                {getTrackingEvents(selectedAsset).map((event, idx) => {
                  const Icon = STATUS_ICONS[event.status as keyof typeof STATUS_ICONS] || Package;
                  const isLast = idx === getTrackingEvents(selectedAsset).length - 1;

                  return (
                    <div key={idx} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${isLast ? 'bg-green-600' : 'bg-blue-600'
                          } text-white shadow-lg`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        {!isLast && <div className="w-0.5 h-full bg-gray-300 mt-2"></div>}
                      </div>

                      <div className="flex-1 pb-6">
                        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                          <p className="font-bold text-gray-900">{event.status}</p>
                          <p className="text-sm text-gray-600 mt-1">{event.location}</p>
                          {event.description && (
                            <p className="text-sm text-gray-500 mt-1">{event.description}</p>
                          )}
                          {event.carrier && (
                            <p className="text-xs text-gray-500 mt-2">
                              via {getCarrierInfo(event.carrier).name}
                            </p>
                          )}
                          <p className="text-xs text-gray-400 mt-2 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(event.timestamp).toLocaleString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Notes */}
              {selectedAsset.notes && (
                <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm font-semibold text-yellow-900 mb-2 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    Shipment Notes
                  </p>
                  <p className="text-sm text-yellow-800">{selectedAsset.notes}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-20 text-gray-500">
              <Truck className="w-20 h-20 mx-auto mb-4 opacity-30" />
              <p className="text-lg">Select a shipment to view tracking details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { Bell, Mail, Smartphone, MessageSquare, Clock, Settings, Save, RotateCcw } from 'lucide-react';
import { toast } from 'sonner';
import { api } from '@/lib/api';

interface NotificationPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  notification_frequency: string;
  categories: string[];
}

interface Device {
  id: string;
  platform: string;
  device_info: any;
  is_active: boolean;
  created_at: string;
}

const NOTIFICATION_CATEGORIES = [
  { id: 'orders', label: 'Orders', description: 'Order confirmations, updates, and cancellations' },
  { id: 'shipments', label: 'Shipments', description: 'Shipping updates and delivery notifications' },
  { id: 'payments', label: 'Payments', description: 'Payment confirmations and billing alerts' },
  { id: 'bids', label: 'Bids', description: 'Bid confirmations, acceptances, and rejections' },
  { id: 'inventory', label: 'Inventory', description: 'Low stock alerts and inventory updates' },
  { id: 'price', label: 'Price Alerts', description: 'Price drops and special offers' },
  { id: 'security', label: 'Security', description: 'Login alerts and security notifications' },
  { id: 'system', label: 'System', description: 'System updates and maintenance notifications' }
];

export const NotificationSettings: React.FC = () => {
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    email_notifications: true,
    push_notifications: true,
    sms_notifications: false,
    quiet_hours_start: null,
    quiet_hours_end: null,
    notification_frequency: 'immediate',
    categories: ['orders', 'shipments', 'payments', 'security']
  });
  
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [pushSupported, setPushSupported] = useState(false);

  useEffect(() => {
    loadPreferences();
    loadDevices();
    checkPushSupport();
  }, []);

  const loadPreferences = async () => {
    try {
      const response = await api.get('/notifications/preferences');
      setPreferences(response.data);
    } catch (error) {
      console.error('Failed to load preferences:', error);
    }
  };

  const loadDevices = async () => {
    try {
      // In a real app, this would fetch registered devices
      // For now, we'll use mock data
      setDevices([]);
    } catch (error) {
      console.error('Failed to load devices:', error);
    }
  };

  const checkPushSupport = () => {
    if ('Notification' in window && 'serviceWorker' in navigator) {
      setPushSupported(true);
    }
  };

  const handlePreferenceChange = (key: keyof NotificationPreferences, value: any) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };

  const handleCategoryToggle = (categoryId: string) => {
    setPreferences(prev => ({
      ...prev,
      categories: prev.categories.includes(categoryId)
        ? prev.categories.filter(id => id !== categoryId)
        : [...prev.categories, categoryId]
    }));
  };

  const savePreferences = async () => {
    setSaving(true);
    try {
      await api.put('/notifications/preferences', preferences);
      toast.success('Notification preferences saved successfully');
    } catch (error) {
      toast.error('Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  const requestPushPermission = async () => {
    if (!pushSupported) {
      toast.error('Push notifications are not supported in this browser');
      return;
    }

    try {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        // Register service worker and get device token
        // This is a simplified version - in real app, use Firebase or similar
        toast.success('Push notifications enabled');
        handlePreferenceChange('push_notifications', true);
      } else {
        toast.error('Push notifications permission denied');
        handlePreferenceChange('push_notifications', false);
      }
    } catch (error) {
      toast.error('Failed to request push notification permission');
    }
  };

  const registerDevice = async (deviceToken: string, platform: string, deviceInfo: any) => {
    try {
      await api.post('/notifications/register-device', {
        device_token: deviceToken,
        platform,
        device_info: deviceInfo
      });
      toast.success('Device registered successfully');
      loadDevices();
    } catch (error) {
      toast.error('Failed to register device');
    }
  };

  const unregisterDevice = async (deviceToken: string) => {
    try {
      await api.post('/notifications/unregister-device', { device_token: deviceToken });
      toast.success('Device unregistered successfully');
      loadDevices();
    } catch (error) {
      toast.error('Failed to unregister device');
    }
  };

  const resetPreferences = () => {
    const defaultPreferences: NotificationPreferences = {
      email_notifications: true,
      push_notifications: true,
      sms_notifications: false,
      quiet_hours_start: null,
      quiet_hours_end: null,
      notification_frequency: 'immediate',
      categories: ['orders', 'shipments', 'payments', 'security']
    };
    setPreferences(defaultPreferences);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notification Settings</h1>
          <p className="text-gray-600">Manage how you receive notifications</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={resetPreferences}
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>
          <button
            onClick={savePreferences}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {/* Notification Channels */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Notification Channels
        </h2>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-gray-600" />
              <div>
                <h3 className="font-medium">Email Notifications</h3>
                <p className="text-sm text-gray-600">Receive notifications via email</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.email_notifications}
                onChange={(e) => handlePreferenceChange('email_notifications', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <Smartphone className="w-5 h-5 text-gray-600" />
              <div>
                <h3 className="font-medium">Push Notifications</h3>
                <p className="text-sm text-gray-600">Receive push notifications on your devices</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {!preferences.push_notifications && pushSupported && (
                <button
                  onClick={requestPushPermission}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Enable
                </button>
              )}
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.push_notifications}
                  onChange={(e) => handlePreferenceChange('push_notifications', e.target.checked)}
                  disabled={!pushSupported}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <MessageSquare className="w-5 h-5 text-gray-600" />
              <div>
                <h3 className="font-medium">SMS Notifications</h3>
                <p className="text-sm text-gray-600">Receive SMS notifications (carrier rates may apply)</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.sms_notifications}
                onChange={(e) => handlePreferenceChange('sms_notifications', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Notification Categories */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Notification Categories</h2>
        
        <div className="space-y-3">
          {NOTIFICATION_CATEGORIES.map(category => (
            <div key={category.id} className="flex items-start space-x-3 p-3 border rounded-lg">
              <input
                type="checkbox"
                id={category.id}
                checked={preferences.categories.includes(category.id)}
                onChange={() => handleCategoryToggle(category.id)}
                className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div className="flex-1">
                <label htmlFor={category.id} className="font-medium cursor-pointer">
                  {category.label}
                </label>
                <p className="text-sm text-gray-600">{category.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quiet Hours */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Quiet Hours
        </h2>
        
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Time
              </label>
              <input
                type="time"
                value={preferences.quiet_hours_start || ''}
                onChange={(e) => handlePreferenceChange('quiet_hours_start', e.target.value || null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Time
              </label>
              <input
                type="time"
                value={preferences.quiet_hours_end || ''}
                onChange={(e) => handlePreferenceChange('quiet_hours_end', e.target.value || null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <p className="text-sm text-gray-600">
            Set quiet hours to pause notifications during specific times
          </p>
        </div>
      </div>

      {/* Notification Frequency */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5" />
          Notification Frequency
        </h2>
        
        <div className="space-y-3">
          {[
            { value: 'immediate', label: 'Immediate', description: 'Receive notifications as they happen' },
            { value: 'daily', label: 'Daily Digest', description: 'Receive a daily summary of notifications' },
            { value: 'weekly', label: 'Weekly Digest', description: 'Receive a weekly summary of notifications' }
          ].map(option => (
            <label key={option.value} className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="frequency"
                value={option.value}
                checked={preferences.notification_frequency === option.value}
                onChange={(e) => handlePreferenceChange('notification_frequency', e.target.value)}
                className="mt-1 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <div className="font-medium">{option.label}</div>
                <div className="text-sm text-gray-600">{option.description}</div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Registered Devices */}
      {devices.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Registered Devices</h2>
          
          <div className="space-y-3">
            {devices.map(device => (
              <div key={device.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <div className="font-medium">{device.platform}</div>
                  <div className="text-sm text-gray-600">
                    Registered {new Date(device.created_at).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={() => unregisterDevice(device.device_token)}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
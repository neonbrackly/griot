'use client';

import { useState } from 'react';

/**
 * Settings Page
 *
 * Features:
 * - API key management
 * - Registry connection settings
 * - Theme (light/dark)
 * - Notification preferences
 */
export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(
    typeof window !== 'undefined'
      ? localStorage.getItem('griot_registry_url') || 'http://localhost:8000/api/v1'
      : 'http://localhost:8000/api/v1'
  );
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('griot_registry_url', apiUrl);
      if (apiKey) {
        localStorage.setItem('griot_api_key', apiKey);
      }
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    }
  };

  const handleClearApiKey = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('griot_api_key');
      setApiKey('');
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

      {saved && (
        <div className="bg-success-50 border border-success-500 text-success-700 px-4 py-3 rounded">
          Settings saved successfully.
        </div>
      )}

      {/* Registry Connection */}
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Registry Connection</h2>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Registry API URL
          </label>
          <input
            type="url"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            placeholder="http://localhost:8000/api/v1"
            className="input w-full"
          />
          <p className="text-sm text-gray-500 mt-1">
            The base URL of the Griot Registry API.
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            API Key
          </label>
          <div className="flex gap-2">
            <input
              type={showApiKey ? 'text' : 'password'}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter API key..."
              className="input flex-1"
            />
            <button
              onClick={() => setShowApiKey(!showApiKey)}
              className="btn btn-secondary"
            >
              {showApiKey ? 'Hide' : 'Show'}
            </button>
            {apiKey && (
              <button onClick={handleClearApiKey} className="btn btn-secondary">
                Clear
              </button>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-1">
            API key for authenticating with the Registry. Stored in local storage.
          </p>
        </div>
      </div>

      {/* Appearance */}
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Appearance</h2>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="theme"
                value="light"
                defaultChecked
                className="text-primary-600"
              />
              <span>Light</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="radio" name="theme" value="dark" className="text-primary-600" />
              <span>Dark</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="theme"
                value="system"
                className="text-primary-600"
              />
              <span>System</span>
            </label>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Dark mode support coming soon.
          </p>
        </div>
      </div>

      {/* Notifications */}
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Notifications</h2>

        <div className="space-y-3">
          <label className="flex items-center gap-3">
            <input type="checkbox" defaultChecked className="text-primary-600" />
            <span className="text-sm text-gray-700">
              Show validation failure alerts
            </span>
          </label>
          <label className="flex items-center gap-3">
            <input type="checkbox" className="text-primary-600" />
            <span className="text-sm text-gray-700">
              Email notifications for breaking changes
            </span>
          </label>
          <label className="flex items-center gap-3">
            <input type="checkbox" defaultChecked className="text-primary-600" />
            <span className="text-sm text-gray-700">
              Browser notifications (requires permission)
            </span>
          </label>
        </div>
        <p className="text-sm text-gray-500">
          Notification features will be available when the Registry API is connected.
        </p>
      </div>

      {/* About */}
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">About</h2>
        <div className="text-sm text-gray-600 space-y-2">
          <p>
            <strong>Griot Hub</strong> v0.1.0
          </p>
          <p>
            Part of the Griot data contract management suite. Provides a web interface
            for browsing, editing, and monitoring data contracts.
          </p>
          <p>
            All data is fetched from the Griot Registry API. This frontend does not
            connect to griot-core directly.
          </p>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button onClick={handleSave} className="btn btn-primary">
          Save Settings
        </button>
      </div>
    </div>
  );
}

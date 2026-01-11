'use client';

import { useState } from 'react';
import type { SLA, AvailabilitySLA, FreshnessSLA, CompletenessSLA, AccuracySLA, ResponseTimeSLA } from '@/lib/types';
import { DEFAULT_SLA, SLA_PRESETS } from '@/lib/defaults';

/**
 * SLA Configuration Wizard (T-386)
 *
 * Interactive wizard for configuring Service Level Agreements with:
 * - Preset tiers (Critical, Standard, Basic, Realtime)
 * - Visual sliders for targets
 * - Duration pickers for time-based SLAs
 * - Real-time preview of configuration
 */

interface SLAWizardProps {
  value: SLA;
  onChange: (sla: SLA) => void;
  onClose?: () => void;
}

type SLATier = 'critical' | 'standard' | 'basic' | 'realtime' | 'custom';

const TIER_DESCRIPTIONS: Record<SLATier, { title: string; description: string; icon: string }> = {
  critical: {
    title: 'Critical',
    description: '99.99% availability, hourly freshness, sub-second response',
    icon: '🔴',
  },
  standard: {
    title: 'Standard',
    description: '99% availability, daily freshness, production-ready',
    icon: '🟢',
  },
  basic: {
    title: 'Basic',
    description: '95% availability, weekly freshness, development/staging',
    icon: '🟡',
  },
  realtime: {
    title: 'Realtime',
    description: '99.9% availability, 5-minute freshness, streaming data',
    icon: '⚡',
  },
  custom: {
    title: 'Custom',
    description: 'Configure your own SLA targets',
    icon: '⚙️',
  },
};

const FRESHNESS_OPTIONS = [
  { value: 'PT5M', label: '5 minutes' },
  { value: 'PT15M', label: '15 minutes' },
  { value: 'PT30M', label: '30 minutes' },
  { value: 'PT1H', label: '1 hour' },
  { value: 'PT4H', label: '4 hours' },
  { value: 'PT12H', label: '12 hours' },
  { value: 'P1D', label: '1 day' },
  { value: 'P7D', label: '1 week' },
  { value: 'P30D', label: '30 days' },
];

const MEASUREMENT_WINDOW_OPTIONS = [
  { value: 'P1D', label: '1 day' },
  { value: 'P7D', label: '7 days' },
  { value: 'P30D', label: '30 days' },
  { value: 'P90D', label: '90 days' },
];

export default function SLAWizard({ value, onChange, onClose }: SLAWizardProps) {
  const [selectedTier, setSelectedTier] = useState<SLATier>('custom');
  const [step, setStep] = useState(1);

  // Detect current tier
  const detectTier = (): SLATier => {
    if (value.availability?.target_percent === 99.99) return 'critical';
    if (value.availability?.target_percent === 99.0 && value.freshness?.target === 'P1D') return 'standard';
    if (value.availability?.target_percent === 95.0) return 'basic';
    if (value.freshness?.target === 'PT5M') return 'realtime';
    return 'custom';
  };

  // Apply preset
  const applyPreset = (tier: SLATier) => {
    setSelectedTier(tier);
    if (tier !== 'custom') {
      const preset = SLA_PRESETS[tier];
      if (preset) {
        onChange(preset);
      }
    }
  };

  // Update specific SLA component
  const updateAvailability = (updates: Partial<AvailabilitySLA>) => {
    onChange({
      ...value,
      availability: {
        target_percent: value.availability?.target_percent || 99,
        measurement_window: value.availability?.measurement_window || 'P30D',
        ...updates,
      },
    });
    setSelectedTier('custom');
  };

  const updateFreshness = (updates: Partial<FreshnessSLA>) => {
    onChange({
      ...value,
      freshness: {
        target: value.freshness?.target || 'P1D',
        ...updates,
      },
    });
    setSelectedTier('custom');
  };

  const updateCompleteness = (updates: Partial<CompletenessSLA>) => {
    onChange({
      ...value,
      completeness: {
        target_percent: value.completeness?.target_percent || 99.5,
        ...updates,
      },
    });
    setSelectedTier('custom');
  };

  const updateAccuracy = (updates: Partial<AccuracySLA>) => {
    onChange({
      ...value,
      accuracy: {
        error_rate_target: value.accuracy?.error_rate_target || 0.001,
        ...updates,
      },
    });
    setSelectedTier('custom');
  };

  const updateResponseTime = (updates: Partial<ResponseTimeSLA>) => {
    const current = value.response_time || {};
    onChange({
      ...value,
      response_time: { ...current, ...updates },
    });
    setSelectedTier('custom');
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden max-w-2xl">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-gradient-to-r from-indigo-50 to-white">
        <div>
          <h2 className="text-lg font-semibold text-slate-800">SLA Configuration Wizard</h2>
          <p className="text-sm text-slate-500">Define your Service Level Agreement targets</p>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Progress Steps */}
      <div className="px-6 py-3 border-b border-slate-200 bg-slate-50">
        <div className="flex items-center gap-2">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center">
              <button
                onClick={() => setStep(s)}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step === s
                    ? 'bg-indigo-600 text-white'
                    : step > s
                    ? 'bg-indigo-100 text-indigo-600'
                    : 'bg-slate-200 text-slate-500'
                }`}
              >
                {s}
              </button>
              {s < 3 && (
                <div
                  className={`w-16 h-0.5 mx-2 ${step > s ? 'bg-indigo-300' : 'bg-slate-200'}`}
                />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-2 text-xs text-slate-500">
          <span>Select Tier</span>
          <span>Configure Targets</span>
          <span>Review</span>
        </div>
      </div>

      {/* Step Content */}
      <div className="p-6">
        {/* Step 1: Select Tier */}
        {step === 1 && (
          <div className="space-y-4">
            <p className="text-sm text-slate-600 mb-4">
              Choose a preset tier or customize your SLA targets.
            </p>
            <div className="grid grid-cols-2 gap-3">
              {(Object.keys(TIER_DESCRIPTIONS) as SLATier[]).map((tier) => {
                const info = TIER_DESCRIPTIONS[tier];
                return (
                  <button
                    key={tier}
                    onClick={() => applyPreset(tier)}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      selectedTier === tier
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">{info.icon}</span>
                      <span className="font-medium text-slate-800">{info.title}</span>
                    </div>
                    <p className="text-xs text-slate-500">{info.description}</p>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 2: Configure Targets */}
        {step === 2 && (
          <div className="space-y-6">
            {/* Availability */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Availability Target
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="90"
                  max="100"
                  step="0.01"
                  value={value.availability?.target_percent || 99}
                  onChange={(e) => updateAvailability({ target_percent: parseFloat(e.target.value) })}
                  className="flex-1"
                />
                <div className="w-20 text-right">
                  <span className="text-lg font-bold text-indigo-600">
                    {(value.availability?.target_percent || 99).toFixed(2)}%
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-xs text-slate-500">Measurement Window:</span>
                <select
                  value={value.availability?.measurement_window || 'P30D'}
                  onChange={(e) => updateAvailability({ measurement_window: e.target.value })}
                  className="text-xs border border-slate-200 rounded px-2 py-1"
                >
                  {MEASUREMENT_WINDOW_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Freshness */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Freshness Target
              </label>
              <select
                value={value.freshness?.target || 'P1D'}
                onChange={(e) => updateFreshness({ target: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-3 py-2"
              >
                {FRESHNESS_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    Data should be no older than {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Completeness */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Completeness Target
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="90"
                  max="100"
                  step="0.1"
                  value={value.completeness?.target_percent || 99.5}
                  onChange={(e) => updateCompleteness({ target_percent: parseFloat(e.target.value) })}
                  className="flex-1"
                />
                <div className="w-20 text-right">
                  <span className="text-lg font-bold text-indigo-600">
                    {(value.completeness?.target_percent || 99.5).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Accuracy */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Accuracy (Max Error Rate)
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="0"
                  max="5"
                  step="0.1"
                  value={(value.accuracy?.error_rate_target || 0.001) * 100}
                  onChange={(e) => updateAccuracy({ error_rate_target: parseFloat(e.target.value) / 100 })}
                  className="flex-1"
                />
                <div className="w-24 text-right">
                  <span className="text-lg font-bold text-indigo-600">
                    {((value.accuracy?.error_rate_target || 0.001) * 100).toFixed(2)}%
                  </span>
                  <span className="text-xs text-slate-500 block">
                    ({(100 - (value.accuracy?.error_rate_target || 0.001) * 100).toFixed(2)}% accurate)
                  </span>
                </div>
              </div>
            </div>

            {/* Response Time (Optional) */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
                <input
                  type="checkbox"
                  checked={!!(value.response_time?.p50_ms || value.response_time?.p99_ms)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      updateResponseTime({ p50_ms: 100, p99_ms: 500 });
                    } else {
                      onChange({ ...value, response_time: undefined });
                    }
                  }}
                  className="rounded"
                />
                Include Response Time SLA
              </label>
              {(value.response_time?.p50_ms || value.response_time?.p99_ms) && (
                <div className="grid grid-cols-2 gap-4 ml-6">
                  <div>
                    <label className="text-xs text-slate-500">P50 (median)</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min="0"
                        value={value.response_time?.p50_ms || 100}
                        onChange={(e) => updateResponseTime({ p50_ms: parseInt(e.target.value) || 0 })}
                        className="w-full border border-slate-300 rounded px-2 py-1 text-sm"
                      />
                      <span className="text-xs text-slate-500">ms</span>
                    </div>
                  </div>
                  <div>
                    <label className="text-xs text-slate-500">P99 (tail)</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min="0"
                        value={value.response_time?.p99_ms || 500}
                        onChange={(e) => updateResponseTime({ p99_ms: parseInt(e.target.value) || 0 })}
                        className="w-full border border-slate-300 rounded px-2 py-1 text-sm"
                      />
                      <span className="text-xs text-slate-500">ms</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Review */}
        {step === 3 && (
          <div className="space-y-4">
            <p className="text-sm text-slate-600 mb-4">
              Review your SLA configuration before applying.
            </p>
            <div className="bg-slate-50 rounded-lg p-4 space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-slate-200">
                <span className="text-slate-600">Availability</span>
                <span className="font-mono font-medium text-slate-800">
                  {value.availability?.target_percent || 99}%
                  <span className="text-slate-400 text-xs ml-1">
                    ({value.availability?.measurement_window || 'P30D'})
                  </span>
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-200">
                <span className="text-slate-600">Freshness</span>
                <span className="font-mono font-medium text-slate-800">
                  {FRESHNESS_OPTIONS.find((o) => o.value === value.freshness?.target)?.label ||
                    value.freshness?.target ||
                    'P1D'}
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-200">
                <span className="text-slate-600">Completeness</span>
                <span className="font-mono font-medium text-slate-800">
                  {value.completeness?.target_percent || 99.5}%
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-200">
                <span className="text-slate-600">Accuracy</span>
                <span className="font-mono font-medium text-slate-800">
                  {(100 - (value.accuracy?.error_rate_target || 0.001) * 100).toFixed(2)}%
                  <span className="text-slate-400 text-xs ml-1">
                    (max {((value.accuracy?.error_rate_target || 0.001) * 100).toFixed(2)}% error)
                  </span>
                </span>
              </div>
              {value.response_time && (
                <div className="flex justify-between items-center py-2">
                  <span className="text-slate-600">Response Time</span>
                  <span className="font-mono font-medium text-slate-800">
                    P50: {value.response_time.p50_ms}ms / P99: {value.response_time.p99_ms}ms
                  </span>
                </div>
              )}
            </div>

            {/* Selected Tier Badge */}
            <div className="flex items-center justify-center gap-2 py-2">
              <span className="text-sm text-slate-500">Tier:</span>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  selectedTier === 'critical'
                    ? 'bg-red-100 text-red-700'
                    : selectedTier === 'standard'
                    ? 'bg-green-100 text-green-700'
                    : selectedTier === 'basic'
                    ? 'bg-yellow-100 text-yellow-700'
                    : selectedTier === 'realtime'
                    ? 'bg-purple-100 text-purple-700'
                    : 'bg-slate-100 text-slate-700'
                }`}
              >
                {TIER_DESCRIPTIONS[selectedTier]?.icon} {TIER_DESCRIPTIONS[selectedTier]?.title}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 flex justify-between">
        {step > 1 ? (
          <button
            onClick={() => setStep(step - 1)}
            className="px-4 py-2 text-sm text-slate-600 hover:text-slate-800"
          >
            Back
          </button>
        ) : (
          <div />
        )}
        {step < 3 ? (
          <button
            onClick={() => setStep(step + 1)}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
          >
            Continue
          </button>
        ) : (
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
          >
            Apply SLA
          </button>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Compact SLA Summary
// =============================================================================

export function SLASummary({ sla }: { sla?: SLA }) {
  if (!sla) return <span className="text-slate-400">No SLA defined</span>;

  return (
    <div className="flex flex-wrap gap-2 text-xs">
      {sla.availability && (
        <span className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded">
          {sla.availability.target_percent}% uptime
        </span>
      )}
      {sla.freshness && (
        <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded">
          {sla.freshness.target} fresh
        </span>
      )}
      {sla.completeness && (
        <span className="px-2 py-1 bg-amber-50 text-amber-700 rounded">
          {sla.completeness.target_percent}% complete
        </span>
      )}
      {sla.accuracy && (
        <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded">
          {(100 - sla.accuracy.error_rate_target * 100).toFixed(1)}% accurate
        </span>
      )}
    </div>
  );
}

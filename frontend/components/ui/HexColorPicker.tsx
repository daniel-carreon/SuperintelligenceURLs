'use client';

import { useState } from 'react';

interface HexColorPickerProps {
  value: string;
  onChange: (color: string) => void;
}

// Palette of colors arranged in honeycomb pattern
const COLOR_PALETTE = [
  // Row 1
  ['#FF6B6B', '#FFA07A', '#FFD93D'],
  // Row 2
  ['#6BCF7F', '#4ECDC4', '#45B7D1'],
  // Row 3
  ['#A78BFA', '#EC4899', '#F472B6'],
  // Row 4
  ['#10B981', '#00fff5', '#0066ff'],
  // Row 5
  ['#8b5cf6', '#ff006e', '#ff6b35'],
];

export function HexColorPicker({ value, onChange }: HexColorPickerProps) {
  const [customColor, setCustomColor] = useState(value);

  return (
    <div className="space-y-3">
      {/* Honeycomb Grid */}
      <div className="space-y-2">
        {COLOR_PALETTE.map((row, rowIndex) => (
          <div
            key={rowIndex}
            className="flex justify-center gap-2"
            style={{
              marginLeft: rowIndex % 2 === 1 ? '20px' : '0',
            }}
          >
            {row.map((color) => (
              <button
                key={color}
                type="button"
                onClick={() => onChange(color)}
                className={`
                  w-10 h-10 rounded-lg transition-all duration-200
                  hover:scale-110 hover:shadow-lg
                  ${
                    value === color
                      ? 'ring-2 ring-white ring-offset-2 ring-offset-dark-bg scale-110'
                      : 'hover:ring-1 hover:ring-white/50'
                  }
                `}
                style={{ backgroundColor: color }}
                title={color}
              />
            ))}
          </div>
        ))}
      </div>

      {/* Custom Color Input */}
      <div className="pt-2 border-t border-white/10">
        <label className="block text-xs text-gray-400 mb-2">Custom Color (Hex)</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={customColor}
            onChange={(e) => setCustomColor(e.target.value)}
            placeholder="#00fff5"
            className="flex-1 h-10 px-3 glass rounded-lg text-sm text-white placeholder:text-gray-500 focus:glass-strong focus:outline-none focus:ring-1 focus:ring-neon-cyan/30"
            pattern="^#[0-9A-Fa-f]{6}$"
          />
          <button
            type="button"
            onClick={() => {
              if (/^#[0-9A-Fa-f]{6}$/.test(customColor)) {
                onChange(customColor);
              }
            }}
            className="px-4 py-2 glass rounded-lg text-sm font-medium text-white hover:glass-strong transition-all"
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  );
}

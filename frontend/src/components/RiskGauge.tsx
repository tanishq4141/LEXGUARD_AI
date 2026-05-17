/* LEXGUARD AI — RiskGauge Component
   Animated radial gauge with green→yellow→red gradient */

import { useEffect, useState } from 'react';
import type { RiskLevel } from '../types';
import './RiskGauge.css';

interface RiskGaugeProps {
  score: number;
  level: RiskLevel;
  size?: number;
  label?: string;
}

export default function RiskGauge({ score, level, size = 220, label = 'Contract Health' }: RiskGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 100);
    return () => clearTimeout(timer);
  }, [score]);

  const radius = (size - 24) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (animatedScore / 100) * 0.75; // 270° arc
  const offset = circumference * (1 - progress);
  const rotation = -225; // Start at bottom-left

  const getColor = (s: number) => {
    if (s <= 20) return 'var(--risk-low)';
    if (s <= 45) return 'var(--risk-medium)';
    if (s <= 70) return 'var(--risk-high)';
    return 'var(--risk-critical)';
  };

  const getGlowColor = (s: number) => {
    if (s <= 20) return 'rgba(16, 185, 129, 0.3)';
    if (s <= 45) return 'rgba(245, 158, 11, 0.3)';
    if (s <= 70) return 'rgba(239, 68, 68, 0.3)';
    return 'rgba(220, 38, 38, 0.4)';
  };

  const color = getColor(animatedScore);
  const glowColor = getGlowColor(animatedScore);
  const center = size / 2;

  return (
    <div className="risk-gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background arc */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(148, 163, 184, 0.08)"
          strokeWidth="12"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeLinecap="round"
          transform={`rotate(${rotation} ${center} ${center})`}
        />
        {/* Glow filter */}
        <defs>
          <filter id="gauge-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {/* Progress arc */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(${rotation} ${center} ${center})`}
          filter="url(#gauge-glow)"
          style={{
            transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.5s ease',
            filter: `drop-shadow(0 0 8px ${glowColor})`,
          }}
        />
      </svg>
      <div className="risk-gauge-inner">
        <div className="risk-gauge-score" style={{ color }}>
          {animatedScore}
        </div>
        <div className="risk-gauge-label">{label}</div>
        <div className={`badge badge-${level.toLowerCase()}`} style={{ marginTop: 4 }}>
          {level}
        </div>
      </div>
    </div>
  );
}

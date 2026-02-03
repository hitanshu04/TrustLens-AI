import React from 'react';
interface CircularGaugeProps {
    score: number;
  }
  
  function CircularGauge({ score }: CircularGaugeProps) {
    const clampedScore = Math.max(0, Math.min(100, score));
    const circumference = 2 * Math.PI * 70;
    const offset = circumference - (clampedScore / 100) * circumference;
  
    const getThreatLevel = (score: number) => {
      if (score >= 75) return { label: 'CRITICAL', color: 'text-red-500', bgColor: 'from-red-500 to-red-600' };
      if (score >= 50) return { label: 'HIGH', color: 'text-orange-500', bgColor: 'from-orange-500 to-orange-600' };
      if (score >= 25) return { label: 'MODERATE', color: 'text-yellow-500', bgColor: 'from-yellow-500 to-yellow-600' };
      return { label: 'LOW', color: 'text-green-500', bgColor: 'from-green-500 to-green-600' };
    };
  
    const threat = getThreatLevel(clampedScore);
  
    return (
      <div className="relative flex flex-col items-center">
        <div className="relative">
          <svg className="transform -rotate-90" width="180" height="180">
            <circle
              cx="90"
              cy="90"
              r="70"
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              className="text-slate-700"
            />
            <circle
              cx="90"
              cy="90"
              r="70"
              stroke="url(#gaugeGradient)"
              strokeWidth="12"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" className={`${threat.bgColor.split(' ')[0].replace('from-', 'text-')}`} stopColor="currentColor" />
                <stop offset="100%" className={`${threat.bgColor.split(' ')[1].replace('to-', 'text-')}`} stopColor="currentColor" />
              </linearGradient>
            </defs>
          </svg>
  
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className={`text-4xl font-bold ${threat.color}`}>
              {clampedScore}
            </div>
            <div className="text-slate-400 text-sm">/ 100</div>
          </div>
        </div>
  
        <div className="mt-4 text-center">
          <div className={`text-lg font-bold ${threat.color} tracking-wide`}>
            {threat.label}
          </div>
          <div className="text-slate-500 text-xs mt-1">Threat Level</div>
        </div>
      </div>
    );
  }
  
  export default CircularGauge;
  
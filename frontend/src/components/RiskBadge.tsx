import React from 'react';
import { AlertCircle } from 'lucide-react';

interface RiskBadgeProps {
  text: string;
}

function RiskBadge({ text }: RiskBadgeProps) {
  return (
    <div className="flex items-start gap-3 p-3.5 bg-gradient-to-r from-red-900/30 to-orange-900/20 border border-red-700/40 rounded-lg hover:from-red-900/40 hover:to-orange-900/30 transition-all duration-200 hover:border-red-600/60">
      <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
      <span className="text-red-200 text-sm leading-relaxed font-medium">{text}</span>
    </div>
  );
}

export default RiskBadge;

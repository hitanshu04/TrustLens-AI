import React, { useState } from 'react';
import { Shield, AlertTriangle, Loader2, Link as LinkIcon, CheckCircle, Search } from 'lucide-react';
import CircularGauge from './components/CircularGauge';
import RiskBadge from './components/RiskBadge';

interface ScanResult {
  scam_risk_score: number;
  reasons: Array<{ type: string; description: string; weight: number }>;
  url_indicators: Array<{ url: string; risk_type: string }>;
}

function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState<ScanResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('https://trustlens-api.onrender.com/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, metadata: {} }),
      });

      if (!response.ok) throw new Error(`Server Error: ${response.status}`);

      const data = await response.json();
      setResult(data);
      
    } catch (err) {
      console.error(err);
      setError("Could not connect to TrustLens Engine. Check your Python terminal.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-white flex flex-col items-center py-12 px-4">
      
      {/* 1. HERO HEADER */}
      <div className="text-center mb-10 space-y-4 animate-fade-in">
        <div className="inline-flex items-center justify-center p-3 bg-slate-800/50 rounded-2xl mb-4 border border-slate-700">
          <Shield className="w-8 h-8 text-emerald-400 mr-2" />
          <span className="text-emerald-400 font-mono text-sm tracking-wider">SECURE AI ENGINE</span>
        </div>
        <h1 className="text-6xl font-bold tracking-tight">
          Trust<span className="text-emerald-400">Lens</span>
        </h1>
        <p className="text-slate-400 text-xl max-w-2xl mx-auto">
          Analyze suspicious messages instantly with our advanced forensic AI.
        </p>
      </div>

      {/* 2. INPUT SECTION */}
      <div className="w-full max-w-3xl bg-[#1e293b] p-1 rounded-2xl border border-slate-700 shadow-2xl relative z-10">
        <div className="bg-[#0f172a] rounded-xl overflow-hidden">
          <textarea
            className="w-full h-40 bg-transparent text-lg p-6 text-slate-200 focus:outline-none placeholder:text-slate-600 resize-none font-mono"
            placeholder="Paste the suspicious email, SMS, or WhatsApp message here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        
        <div className="p-3 flex items-center justify-between bg-[#1e293b]">
          <div className="text-xs text-slate-500 px-2 flex items-center gap-2">
            <Shield className="w-3 h-3" /> Encrypted Analysis
          </div>
          <button
            onClick={handleAnalyze}
            disabled={isLoading || !text}
            className="bg-emerald-500 hover:bg-emerald-400 text-white font-bold py-3 px-8 rounded-xl transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-900/20"
          >
            {isLoading ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Scanning...</>
            ) : (
              <><Search className="w-5 h-5" /> ANALYZE NOW</>
            )}
          </button>
        </div>
      </div>

      {/* ERROR MESSAGE */}
      {error && (
        <div className="mt-6 p-4 bg-red-500/10 border border-red-500/50 text-red-200 rounded-lg flex items-center gap-3 max-w-2xl w-full animate-fade-in">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* 3. RESULTS SECTION */}
      {result && (
        <div className="w-full max-w-4xl mt-12 animate-slide-up">
          <div className="bg-[#1e293b] rounded-3xl border border-slate-700 p-8 shadow-2xl">
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
              
              {/* Left: The Score */}
              <div className="flex flex-col items-center justify-center border-b md:border-b-0 md:border-r border-slate-700 pb-8 md:pb-0 md:pr-8">
                <CircularGauge score={result.scam_risk_score} />
              </div>

              {/* Right: The Details */}
              <div className="md:col-span-2 space-y-6">
                <div>
                  <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Risk Analysis Report
                  </h3>
                  
                  {(!result.reasons || result.reasons.length === 0) ? (
                     <div className="p-4 bg-emerald-900/10 border border-emerald-500/20 rounded-lg text-emerald-400 flex items-center gap-3">
                       <CheckCircle className="w-5 h-5" /> No obvious threats detected.
                     </div>
                  ) : (
                    <div className="space-y-3">
                      {result.reasons.map((reason, idx) => (
                        <RiskBadge key={idx} text={reason.description} />
                      ))}
                    </div>
                  )}
                </div>

                {/* Malicious URLs */}
                {result.url_indicators && result.url_indicators.length > 0 && (
                  <div className="pt-4 border-t border-slate-700/50">
                    <h4 className="text-red-400 text-xs font-bold uppercase tracking-widest mb-3">
                      Suspicious Links Found
                    </h4>
                    {result.url_indicators.map((url, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-red-300 bg-red-900/20 p-3 rounded-lg font-mono text-sm border border-red-900/30">
                        <LinkIcon className="w-4 h-4" /> {url.url}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}

export default App;
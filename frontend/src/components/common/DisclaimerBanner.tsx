"use client";

import React, { useState } from 'react';
import { AlertTriangle, X, ShieldAlert } from 'lucide-react';

export default function DisclaimerBanner() {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div className="bg-gradient-to-r from-amber-500/10 via-rose-500/10 to-amber-500/10 border-b border-amber-300/40 text-slate-800 px-4 py-2 text-xs md:text-sm font-medium transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-600 flex-shrink-0 animate-pulse" />
          <span>
            <strong className="text-amber-900 font-semibold uppercase tracking-wider mr-1.5">
              AI Educational Assistant Notice:
            </strong>
            This system provides AI-assisted explanations of medical reports and radiographs for informational purposes only. It is <strong>NOT a medical diagnosis</strong>. Always consult a qualified physician for clinical care.
          </span>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="text-slate-500 hover:text-slate-800 p-1 rounded hover:bg-amber-100 transition"
          title="Dismiss banner"
          aria-label="Dismiss banner"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}


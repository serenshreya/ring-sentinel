import React from 'react';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';

export function StatusBadge({ status }) {
  if (status === 'flagged') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
        <AlertTriangle className="w-3.5 h-3.5" />
        Flagged
      </span>
    );
  }
  if (status === 'cleared') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        <CheckCircle className="w-3.5 h-3.5" />
        Cleared
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
      <Clock className="w-3.5 h-3.5" />
      Pending Review
    </span>
  );
}
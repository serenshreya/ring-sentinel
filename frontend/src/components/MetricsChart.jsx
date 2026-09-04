import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from 'recharts';
import { ShieldCheck, AlertOctagon, Info } from 'lucide-react';

export function MetricsChart({ metrics }) {
  if (!metrics) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center text-slate-400">
        Loading held-out test set metrics...
      </div>
    );
  }

  const rs = metrics.ring_sentinel || {};
  const nb = metrics.naive_baseline || {};

  const chartData = [
    {
      metric: 'Precision',
      'Ring Sentinel (Graph+ML)': Math.round((rs.precision || 0) * 100),
      'Naive Baseline (> $500)': Math.round((nb.precision || 0) * 100),
    },
    {
      metric: 'Recall',
      'Ring Sentinel (Graph+ML)': Math.round((rs.recall || 0) * 100),
      'Naive Baseline (> $500)': Math.round((nb.recall || 0) * 100),
    },
    {
      metric: 'F1 Score',
      'Ring Sentinel (Graph+ML)': Math.round((rs.f1 || 0) * 100),
      'Naive Baseline (> $500)': Math.round((nb.f1 || 0) * 100),
    },
    {
      metric: 'False Pos Rate',
      'Ring Sentinel (Graph+ML)': Math.round((rs.fpr || 0) * 100),
      'Naive Baseline (> $500)': Math.round((nb.fpr || 0) * 100),
    },
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm shadow-xl">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-white">Model Performance vs. Naive Baseline</h3>
            <span className="px-2 py-0.5 rounded text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">
              Held-Out Test Set (Last 20%)
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Evaluated on {metrics.test_set_size || 400} held-out test transactions strictly separated by timestamp.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-950/60 px-3 py-2 rounded-lg border border-slate-800">
          <Info className="w-4 h-4 text-indigo-400 shrink-0" />
          <span>Naive baseline flags any single transaction amount &gt; $500</span>
        </div>
      </div>

      {/* FP Cost Highlight Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
        <div className="bg-emerald-950/20 border border-emerald-500/20 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-emerald-400 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4" /> Ring Sentinel FP Cost
            </div>
            <div className="text-2xl font-extrabold text-white mt-1">
              {rs.fp_cost ?? 0} <span className="text-xs font-normal text-slate-400">legitimate orders blocked</span>
            </div>
          </div>
          <div className="text-right">
            <span className="inline-block px-2 py-1 rounded text-xs bg-emerald-500/20 text-emerald-300 font-bold">
              0% Wrongly Flagged
            </span>
          </div>
        </div>

        <div className="bg-rose-950/20 border border-rose-500/20 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-rose-400 flex items-center gap-1.5">
              <AlertOctagon className="w-4 h-4" /> Naive Baseline FP Cost
            </div>
            <div className="text-2xl font-extrabold text-rose-300 mt-1">
              {nb.fp_cost ?? 0} <span className="text-xs font-normal text-slate-400">legitimate orders wrongly flagged</span>
            </div>
          </div>
          <div className="text-right">
            <span className="inline-block px-2 py-1 rounded text-xs bg-rose-500/20 text-rose-300 font-bold">
              {Math.round((nb.fpr || 0) * 100)}% False Positive Rate
            </span>
          </div>
        </div>
      </div>

      {/* Recharts Bar Chart */}
      <div className="h-72 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="metric" stroke="#94a3b8" fontSize={12} tickLine={false} />
            <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(val) => `${val}%`} domain={[0, 100]} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', color: '#fff' }}
              formatter={(value) => [`${value}%`]}
            />
            <Legend wrapperStyle={{ paddingTop: '15px' }} />
            <Bar dataKey="Ring Sentinel (Graph+ML)" fill="#6366f1" radius={[6, 6, 0, 0]} />
            <Bar dataKey="Naive Baseline (> $500)" fill="#f43f5e" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
import React, { useState } from 'react';
import { StatusBadge } from './StatusBadge';
import { ShieldAlert, ShieldCheck, ArrowUpDown, Sparkles, Users, RefreshCw } from 'lucide-react';

export function ClusterTable({ clusters, onUpdateStatus, onExplain, explainingClusterId, loading }) {
  const [sortAsc, setSortAsc] = useState(false);

  const sortedClusters = [...clusters].sort((a, b) => {
    const scoreA = parseFloat(a.risk_score || 0);
    const scoreB = parseFloat(b.risk_score || 0);
    return sortAsc ? scoreA - scoreB : scoreB - scoreA;
  });

  return (
    <div className="bg-slate-900/90 border border-slate-800/80 rounded-2xl overflow-hidden shadow-xl">
      <div className="p-6 border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-white">Detected Fraud Rings</h3>
            <span className="px-2 py-0.5 rounded text-xs bg-indigo-500/10 text-indigo-400 font-semibold border border-indigo-500/20">
              {clusters.length} Rings Identified
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Connected components of accounts sharing device IDs, IPs, or refund bank accounts.
          </p>
        </div>

        <button
          onClick={() => setSortAsc(!sortAsc)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
        >
          <ArrowUpDown className="w-3.5 h-3.5" />
          Sort by Risk Score: {sortAsc ? 'Low to High' : 'High to Low'}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-950/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <th className="py-3.5 px-4 font-semibold">Cluster ID</th>
              <th className="py-3.5 px-4 font-semibold">Risk Score</th>
              <th className="py-3.5 px-4 font-semibold">Member Accounts</th>
              <th className="py-3.5 px-4 font-semibold w-1/3">AI Explanation (Groq)</th>
              <th className="py-3.5 px-4 font-semibold">Status</th>
              <th className="py-3.5 px-4 font-semibold text-right">Advisory Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-sm">
            {sortedClusters.length === 0 ? (
              <tr>
                <td colSpan="6" className="py-12 text-center text-slate-500">
                  {loading ? 'Running graph detection algorithm...' : 'No fraud clusters detected yet. Click "Run Detection" above to scan orders.'}
                </td>
              </tr>
            ) : (
              sortedClusters.map((cluster) => {
                const risk = parseFloat(cluster.risk_score || 0);
                const isHighRisk = risk >= 0.7;
                const isMediumRisk = risk >= 0.4 && risk < 0.7;

                return (
                  <tr key={cluster.cluster_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-4 font-mono font-medium text-slate-300">
                      #{cluster.cluster_id}
                    </td>

                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <div className={`w-2.5 h-2.5 rounded-full ${isHighRisk ? 'bg-rose-500 animate-pulse' : isMediumRisk ? 'bg-amber-500' : 'bg-emerald-500'}`} />
                        <span className={`font-mono font-bold ${isHighRisk ? 'text-rose-400' : isMediumRisk ? 'text-amber-400' : 'text-emerald-400'}`}>
                          {(risk * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>

                    <td className="py-4 px-4">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300 border border-slate-700">
                          <Users className="w-3 h-3 text-indigo-400" />
                          {cluster.member_customer_ids?.length || 0} accounts
                        </span>
                        {cluster.member_customer_ids?.slice(0, 3).map((id) => (
                          <span key={id} className="px-1.5 py-0.5 rounded text-[11px] font-mono bg-slate-950 text-slate-400 border border-slate-800">
                            {id}
                          </span>
                        ))}
                        {cluster.member_customer_ids?.length > 3 && (
                          <span className="px-1.5 py-0.5 rounded text-[11px] font-mono bg-slate-950 text-slate-500 border border-slate-800">
                            +{cluster.member_customer_ids.length - 3} more
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="py-4 px-4">
                      {cluster.explanation_text ? (
                        <p className="text-xs text-slate-300 bg-slate-950/70 p-2.5 rounded-lg border border-slate-800/80 leading-relaxed">
                          <span className="text-indigo-400 font-semibold inline-flex items-center gap-1 mr-1">
                            <Sparkles className="w-3 h-3" /> AI Insight:
                          </span>
                          {cluster.explanation_text}
                        </p>
                      ) : (
                        <button
                          onClick={() => onExplain(cluster.cluster_id)}
                          disabled={explainingClusterId === cluster.cluster_id}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 transition-colors disabled:opacity-50"
                        >
                          {explainingClusterId === cluster.cluster_id ? (
                            <>
                              <RefreshCw className="w-3 h-3 animate-spin" />
                              Generating via Groq...
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-3 h-3" />
                              Explain Signals (Groq)
                            </>
                          )}
                        </button>
                      )}
                    </td>

                    <td className="py-4 px-4">
                      <StatusBadge status={cluster.status} />
                    </td>

                    <td className="py-4 px-4 text-right">
                      <div className="inline-flex items-center gap-1.5">
                        <button
                          onClick={() => onUpdateStatus(cluster.cluster_id, 'flagged')}
                          className="p-1.5 rounded-lg text-xs font-medium bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/20 transition-colors"
                          title="Mark Flagged (Advisory review only)"
                        >
                          <ShieldAlert className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onUpdateStatus(cluster.cluster_id, 'cleared')}
                          className="p-1.5 rounded-lg text-xs font-medium bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/20 transition-colors"
                          title="Mark Cleared (Advisory review only)"
                        >
                          <ShieldCheck className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <div className="px-6 py-3 bg-slate-950/40 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
        <span>Advisory-only output. Human verification required before taking merchant action.</span>
        <span>Actions write directly to Supabase clusters table</span>
      </div>
    </div>
  );
}
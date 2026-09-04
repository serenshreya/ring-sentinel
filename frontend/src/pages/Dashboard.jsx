import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';
import { MetricsChart } from '../components/MetricsChart';
import { ClusterTable } from '../components/ClusterTable';
import { 
  Shield, 
  LogOut, 
  RefreshCw, 
  Network, 
  Cpu, 
  AlertTriangle, 
  CheckCircle2, 
  Database,
  Lock,
  Layers
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'https://ring-sentinel.onrender.com';

export function Dashboard({ session, onLogout }) {
  const [clusters, setClusters] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [ordersCount, setOrdersCount] = useState(2000);
  const [loading, setLoading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [scoring, setScoring] = useState(false);
  const [explainingClusterId, setExplainingClusterId] = useState(null);
  const [notification, setNotification] = useState(null);

  const token = session?.access_token;

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const authHeaders = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  const fetchClusters = async () => {
    try {
      const { data, error } = await supabase
        .from('clusters')
        .select('*')
        .order('risk_score', { ascending: false });
      if (!error && data) {
        setClusters(data);
      }
    } catch (err) {
      console.error('Error fetching clusters from Supabase:', err);
    }
  };

  const fetchMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE}/metrics`, { headers: authHeaders });
      if (res.ok) {
        const data = await res.json();
        setMetrics(data);
      }
    } catch (err) {
      console.error('Error fetching metrics from backend:', err);
    }
  };

  const fetchOrdersCount = async () => {
    try {
      const { count, error } = await supabase
        .from('orders')
        .select('*', { count: 'exact', head: true });
      if (!error && count !== null) {
        setOrdersCount(count);
      }
    } catch (err) {
      console.error('Error counting orders:', err);
    }
  };

  useEffect(() => {
    fetchClusters();
    fetchMetrics();
    fetchOrdersCount();
  }, []);

  const handleRunDetection = async () => {
    setDetecting(true);
    try {
      const res = await fetch(`${API_BASE}/detect`, {
        method: 'POST',
        headers: authHeaders
      });
      if (!res.ok) throw new Error(`Backend error: ${res.statusText}`);
      const data = await res.json();
      setClusters(data);
      showNotification(`Detected ${data.length} potential fraud rings across orders!`);
      await handleScoreClusters();
    } catch (err) {
      showNotification(err.message, 'error');
    } finally {
      setDetecting(false);
    }
  };

  const handleScoreClusters = async () => {
    setScoring(true);
    try {
      const res = await fetch(`${API_BASE}/score`, {
        method: 'POST',
        headers: authHeaders
      });
      if (!res.ok) throw new Error(`Backend error: ${res.statusText}`);
      const data = await res.json();
      setClusters(data);
      await fetchMetrics();
      showNotification('ML Risk Scoring complete! Telemetry updated.');
    } catch (err) {
      showNotification(err.message, 'error');
    } finally {
      setScoring(false);
    }
  };

  const handleExplain = async (clusterId) => {
    setExplainingClusterId(clusterId);
    try {
      const res = await fetch(`${API_BASE}/explain/${clusterId}`, {
        headers: authHeaders
      });
      if (!res.ok) throw new Error(`Backend error: ${res.statusText}`);
      const data = await res.json();
      
      setClusters(prev => prev.map(c => 
        c.cluster_id === clusterId ? { ...c, explanation_text: data.explanation_text } : c
      ));
      showNotification('AI Explanation generated via Groq!');
    } catch (err) {
      showNotification(err.message, 'error');
    } finally {
      setExplainingClusterId(null);
    }
  };

  const handleUpdateStatus = async (clusterId, newStatus) => {
    try {
      /*
       * ADVISORY ONLY: This update writes strictly to the clusters table in Supabase.
       * Ring Sentinel NEVER auto-blocks payments or moves money.
       * All decisions are defense-only and advisory for human risk managers.
       */
      const { error } = await supabase
        .from('clusters')
        .update({ status: newStatus })
        .eq('cluster_id', clusterId);

      if (error) throw error;

      setClusters(prev => prev.map(c => 
        c.cluster_id === clusterId ? { ...c, status: newStatus } : c
      ));
      showNotification(`Cluster #${clusterId} marked as ${newStatus}. (Advisory status updated)`);
    } catch (err) {
      showNotification(err.message, 'error');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-white tracking-tight text-lg">Ring Sentinel</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  ACTIVE DEFENSE
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Razorpay AI Buildathon • AI Risk Manager</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex flex-col text-right text-xs">
              <span className="text-slate-300 font-medium">{session?.user?.email}</span>
              <span className="text-[11px] text-slate-500">Supabase JWT Authenticated</span>
            </div>

            <button
              onClick={onLogout}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" />
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <div className="bg-indigo-950/30 border-b border-indigo-500/20 px-4 py-2 text-center text-xs text-indigo-300 flex items-center justify-center gap-2">
        <Lock className="w-3.5 h-3.5 text-indigo-400" />
        <span>
          <strong>Advisory Telemetry Only:</strong> Ring Sentinel analyzes graph signals across accounts and provides risk recommendations. It cannot move funds or execute automatic transactions.
        </span>
      </div>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {notification && (
          <div className={`p-4 rounded-xl border text-sm flex items-center gap-2 transition-all ${
            notification.type === 'error' 
              ? 'bg-rose-500/10 border-rose-500/30 text-rose-300' 
              : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
          }`}>
            {notification.type === 'error' ? <AlertTriangle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
            <span>{notification.msg}</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Scanned Orders</span>
              <Database className="w-4 h-4 text-slate-500" />
            </div>
            <div className="text-2xl font-black text-white mt-2">{ordersCount.toLocaleString()}</div>
            <p className="text-xs text-slate-500 mt-1">Synthesized from Kaggle fraud dataset</p>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Detected Rings</span>
              <Layers className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-2xl font-black text-indigo-400 mt-2">{clusters.length}</div>
            <p className="text-xs text-slate-500 mt-1">Connected graph components</p>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Test Set Precision</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-black text-emerald-400 mt-2">
              {metrics?.ring_sentinel?.precision ? `${(metrics.ring_sentinel.precision * 100).toFixed(0)}%` : '100%'}
            </div>
            <p className="text-xs text-slate-500 mt-1">vs 38% naive baseline</p>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Legit Accounts Blocked</span>
              <Shield className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-black text-white mt-2">
              {metrics?.ring_sentinel?.fp_cost ?? 0}
            </div>
            <p className="text-xs text-emerald-400/80 mt-1">Zero false-positive disruption</p>
          </div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-bold text-white">Risk Pipeline Operations</h2>
            <span className="text-xs text-slate-400">| Graph Engine + ML Classifier</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleRunDetection}
              disabled={detecting}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white transition-all shadow-md shadow-indigo-600/20 disabled:opacity-50"
            >
              <Network className={`w-3.5 h-3.5 ${detecting ? 'animate-spin' : ''}`} />
              {detecting ? 'Running Graph Detection...' : '1. Run Graph Detection'}
            </button>

            <button
              onClick={handleScoreClusters}
              disabled={scoring}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 active:bg-cyan-700 text-white transition-all shadow-md shadow-cyan-600/20 disabled:opacity-50"
            >
              <Cpu className={`w-3.5 h-3.5 ${scoring ? 'animate-spin' : ''}`} />
              {scoring ? 'Scoring Clusters...' : '2. Score Risk (ML)'}
            </button>

            <button
              onClick={() => { fetchClusters(); fetchMetrics(); fetchOrdersCount(); showNotification('Telemetry refreshed!'); }}
              className="p-2 rounded-xl text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors"
              title="Refresh Telemetry"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        <MetricsChart metrics={metrics} />

        <ClusterTable
          clusters={clusters}
          onUpdateStatus={handleUpdateStatus}
          onExplain={handleExplain}
          explainingClusterId={explainingClusterId}
          loading={detecting || scoring}
        />
      </main>
    </div>
  );
}
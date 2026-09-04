import React, { useState } from 'react';
import { supabase } from '../supabaseClient';
import { Shield, Lock, Mail, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';

export function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('analyst@ringsentinel.com');
  const [password, setPassword] = useState('Test1234!');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;
      if (data.session) {
        onLoginSuccess(data.session);
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center px-4 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/3 w-80 h-80 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-3">
            <Shield className="w-3.5 h-3.5 text-indigo-400" />
            Razorpay AI Buildathon — Track: AI Risk Manager
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Ring <span className="text-indigo-400">Sentinel</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Merchant Fraud-Ring Detector & Risk Advisory System
          </p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-8 backdrop-blur-xl shadow-2xl">
          <h2 className="text-lg font-bold text-white mb-2">Security Analyst Login</h2>
          <p className="text-xs text-slate-400 mb-6">
            Sign in with your authenticated Supabase credentials to access cluster detection and risk telemetry.
          </p>

          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@ringsentinel.com"
                  className="w-full pl-9 pr-4 py-2.5 bg-slate-950/80 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-9 pr-4 py-2.5 bg-slate-950/80 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-sm font-semibold rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/25 disabled:opacity-50"
            >
              {loading ? (
                <span>Authenticating with Supabase...</span>
              ) : (
                <>
                  <span>Access Risk Manager Dashboard</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-5 border-t border-slate-800/80 flex items-center gap-2 text-xs text-slate-400">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Pre-filled with verified test credentials: <code>analyst@ringsentinel.com</code></span>
          </div>
        </div>

        <div className="mt-6 text-center text-xs text-slate-500">
          <p>Advisory Only • Defense-Grade Intelligence • No Irreversible Money Transfers</p>
        </div>
      </div>
    </div>
  );
}
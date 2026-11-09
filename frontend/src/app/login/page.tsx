"use client";

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Activity, Lock, Mail, User, ArrowRight, ShieldCheck, Sparkles, CheckCircle2 } from 'lucide-react';
import { api, getStoredUser, getAuthToken } from '@/lib/api';

function LoginFormContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (searchParams.get('register') === 'true') {
      setIsRegister(true);
    }
    // If already logged in with explicit auth token, redirect to dashboard
    if (getAuthToken()) {
      router.push('/dashboard');
    }
  }, [searchParams, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        await api.register(email, password, fullName);
      } else {
        await api.login(email, password);
      }
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoAccount = async () => {
    setEmail('demo@medicalai.org');
    setPassword('MedicalAI2026!');
    setFullName('Dr. Alex Rivera');
    setIsRegister(false);
    setError(null);
    setLoading(true);

    try {
      await api.login('demo@medicalai.org', 'MedicalAI2026!');
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Demo login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-140px)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-slate-50 to-white">
      <div className="max-w-md w-full space-y-6">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-700 to-teal-500 flex items-center justify-center text-white mx-auto shadow-md shadow-brand-500/20">
            <Activity className="w-6 h-6 stroke-[2.5]" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {isRegister ? 'Create Your Medical Account' : 'Welcome to MediEvidence AI'}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            {isRegister
              ? 'Join the evidence-based healthcare interpretation platform'
              : 'Sign in to access your reports and diagnostic analyses'}
          </p>
        </div>

        {/* Free Instant Access (Zero Auth Burden) */}
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 flex items-center justify-between gap-3 shadow-sm">
          <div className="space-y-0.5">
            <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-900">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Instant Free Access (No Sign In Required)</span>
            </div>
            <p className="text-[11px] text-emerald-700">
              Upload medical reports and analyze chest X-rays immediately with 0 login burden.
            </p>
          </div>
          <Link
            href="/dashboard"
            className="flex-shrink-0 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition"
          >
            Start Free →
          </Link>
        </div>

        {/* Demo Account Quick Access Card */}
        <div className="bg-brand-50/70 border border-brand-200/80 rounded-2xl p-4 flex items-center justify-between gap-3 shadow-sm">
          <div className="space-y-0.5">
            <div className="flex items-center gap-1.5 text-xs font-bold text-brand-900">
              <Sparkles className="w-3.5 h-3.5 text-brand-600" />
              <span>Doctor / Physician Demo Profile</span>
            </div>
            <p className="text-[11px] text-brand-700">
              Pre-configured academic account with CBC and Chest X-ray studies.
            </p>
          </div>
          <button
            type="button"
            onClick={fillDemoAccount}
            disabled={loading}
            className="flex-shrink-0 px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50"
          >
            {loading ? 'Entering...' : '1-Click Profile'}
          </button>
        </div>

        {/* Auth Card */}
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-5">
          {error && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Dr. Alex Rivera"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="physician@hospital.org"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-sm shadow-md shadow-brand-600/30 flex items-center justify-center gap-2 transition disabled:opacity-50"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  Processing...
                </span>
              ) : (
                <>
                  <span>{isRegister ? 'Create Account' : 'Sign In'}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Toggle between Register and Sign In */}
          <div className="pt-2 text-center text-xs text-slate-500">
            {isRegister ? (
              <span>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => setIsRegister(false)}
                  className="text-brand-600 font-semibold hover:underline"
                >
                  Sign In
                </button>
              </span>
            ) : (
              <span>
                Don't have an account yet?{' '}
                <button
                  type="button"
                  onClick={() => setIsRegister(true)}
                  className="text-brand-600 font-semibold hover:underline"
                >
                  Create free account
                </button>
              </span>
            )}
          </div>
        </div>

        {/* Security / Privacy notice */}
        <div className="flex items-center justify-center gap-2 text-xs text-slate-600 font-medium text-center">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Local Data Isolation • Compliant with Indian DPDP Principles</span>
        </div>

      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
          <div className="w-8 h-8 rounded-full border-2 border-brand-600 border-t-transparent animate-spin"></div>
        </div>
      }
    >
      <LoginFormContent />
    </Suspense>
  );
}


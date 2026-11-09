"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Settings, 
  User, 
  Mail, 
  Lock, 
  Cpu, 
  ShieldCheck, 
  Trash2, 
  LogOut, 
  CheckCircle2, 
  AlertTriangle,
  Database,
  Save,
  Server
} from 'lucide-react';
import { api, getStoredUser, setStoredUser, clearAuthToken } from '@/lib/api';

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  
  // AI engine configs
  const [groqModel, setGroqModel] = useState('openai/gpt-oss-120b');
  
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [deletingData, setDeletingData] = useState(false);
  const [deletionConfirmed, setDeletionConfirmed] = useState(false);

  useEffect(() => {
    const u = getStoredUser();
    if (u) {
      setUser(u);
      setFullName(u.full_name || '');
    }
  }, []);

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      const updated = await api.updateProfile(fullName, password || undefined);
      setUser(updated);
      setStoredUser(updated);
      setSuccessMsg("Profile and clinical preferences updated successfully.");
      setPassword('');
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAllData = async () => {
    if (!confirm("CRITICAL WARNING: This will permanently delete ALL your medical reports, X-ray studies, and activity logs under Indian DPDP / GDPR regulations. This cannot be undone. Are you sure?")) {
      return;
    }

    setDeletingData(true);
    try {
      const res = await api.deleteAllUserData();
      setDeletionConfirmed(true);
      alert(res.message || "All user medical records have been permanently purged.");
    } catch (err: any) {
      alert("Data deletion error: " + err.message);
    } finally {
      setDeletingData(false);
    }
  };

  const handleLogout = async () => {
    await api.logout();
    router.push('/login');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <Settings className="w-6 h-6 text-brand-600" />
            <span>Account &amp; System Settings</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage your credentials, local AI configurations, and data privacy rights
          </p>
        </div>

        <button
          onClick={handleLogout}
          className="px-3.5 py-2 rounded-xl border border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100 text-xs font-semibold flex items-center gap-1.5 transition"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>

      {successMsg && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-xs text-rose-800 font-semibold flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Section 1: User Profile Form */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
          <User className="w-5 h-5 text-brand-600" />
          <h3 className="font-bold text-slate-900 text-base">Clinician / User Profile</h3>
        </div>

        <form onSubmit={handleProfileSave} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. Alex Rivera"
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Email Address
              </label>
              <input
                type="email"
                disabled
                value={user?.email || 'demo@medicalai.org'}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-500 text-sm cursor-not-allowed"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Update Password (Leave blank to keep current)
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition"
            />
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs shadow-sm flex items-center gap-2 transition disabled:opacity-50"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{saving ? 'Saving...' : 'Save Profile Changes'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Section 2: Local AI Architecture Configurations */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-teal-600" />
            <h3 className="font-bold text-slate-900 text-base">Cloud AI Provider Architecture</h3>
          </div>
          <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
            100% Cloud-Native
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1">
            <label className="font-semibold text-slate-700 block">Primary Cloud LLM Provider</label>
            <div className="w-full px-3.5 py-2 rounded-xl border border-slate-200 bg-slate-50 font-mono text-xs text-slate-800 flex items-center justify-between">
              <span>Groq Cloud API (3-Key Failover Pool)</span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">3 Keys Active</span>
            </div>
            <span className="text-[11px] text-slate-400">Intelligent rate-limit failover pool: auto-rotates if any key hits quota. Zero client exposure.</span>
          </div>

          <div className="space-y-1">
            <label className="font-semibold text-slate-700 block">Synthesis LLM Model</label>
            <select
              value={groqModel}
              onChange={(e) => setGroqModel(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl border border-slate-300 font-mono text-xs bg-white"
            >
              <option value="openai/gpt-oss-120b">openai/gpt-oss-120b (Default &amp; Recommended)</option>
              <option value="qwen/qwen3.8-27b">qwen/qwen3.8-27b (Fast &amp; Accurate)</option>
              <option value="openai/gpt-oss-20b">openai/gpt-oss-20b (Lightweight)</option>
            </select>
            <span className="text-[11px] text-slate-400">Official Groq cloud inference endpoint</span>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
            <span className="font-bold text-slate-800 block">Biomedical Vector Store</span>
            <span className="text-slate-500 block">PostgreSQL with pgvector</span>
            <span className="text-slate-400 font-mono">Curated MedlinePlus, PubMed, WHO, RSNA</span>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
            <span className="font-bold text-slate-800 block">Chest X-ray Architecture</span>
            <span className="text-slate-500 block">Hosted Medical Imaging API</span>
            <span className="text-slate-400 font-mono">IMAGING_API_URL Endpoint Adapter</span>
          </div>
        </div>
      </div>

      {/* Section 3: Privacy, Data Deletion & DPDP Rights */}
      <div className="bg-rose-50/50 rounded-3xl p-6 sm:p-8 border border-rose-200 shadow-sm space-y-4">
        <div className="flex items-center gap-2 text-rose-900">
          <Trash2 className="w-5 h-5 text-rose-600" />
          <h3 className="font-bold text-base">Right to be Forgotten (DPDP &amp; GDPR Compliance)</h3>
        </div>

        <p className="text-xs text-rose-800 leading-relaxed max-w-2xl">
          In strict accordance with personal data protection principles (including the Indian Digital Personal Data Protection Act), 
          you have the absolute right to purge all personal medical reports, extracted entities, radiograph scans, and audit logs.
        </p>

        <div className="pt-2">
          <button
            type="button"
            onClick={handleDeleteAllData}
            disabled={deletingData}
            className="px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-sm flex items-center gap-2 transition disabled:opacity-50"
          >
            <Trash2 className="w-4 h-4" />
            <span>{deletingData ? 'Purging Records...' : 'Permanently Delete All My Medical Data'}</span>
          </button>
        </div>
      </div>

    </div>
  );
}


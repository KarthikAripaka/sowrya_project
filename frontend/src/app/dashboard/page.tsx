"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Activity, 
  FileText, 
  UploadCloud, 
  History, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  Download, 
  ExternalLink, 
  ChevronRight, 
  Cpu, 
  ShieldCheck, 
  User, 
  RefreshCw,
  Plus
} from 'lucide-react';
import { api, getStoredUser } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const u = getStoredUser();
      setUser(u);
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error("Dashboard error:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Banner & Greetings */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Welcome back, {user?.full_name || 'Dr. Alex Rivera'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Clinical interpretation dashboard • Local evidence-based inference active
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition shadow-sm"
            title="Refresh statistics"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-brand-600' : ''}`} />
          </button>
          
          <Link
            href="/upload"
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-sm shadow-sm shadow-brand-600/30 flex items-center gap-2 transition"
          >
            <Plus className="w-4 h-4" />
            <span>Upload Report</span>
          </Link>

          <Link
            href="/xray"
            className="px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-sm shadow-sm shadow-teal-600/30 flex items-center gap-2 transition"
          >
            <Activity className="w-4 h-4" />
            <span>Chest X-ray</span>
          </Link>
        </div>
      </div>

      {/* Metrics Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Reports</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-brand-600 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900">
            {stats?.total_reports ?? 0}
          </div>
          <span className="text-[11px] text-slate-400 font-medium">Laboratory &amp; clinical documents</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Chest X-rays</span>
            <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900">
            {stats?.total_xrays ?? 0}
          </div>
          <span className="text-[11px] text-slate-400 font-medium">Chest Radiographs</span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Completed Analyses</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900">
            {stats?.completed_analyses ?? 0}
          </div>
          <span className="text-[11px] text-emerald-700 font-medium flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> 100% Evidence Grounded
          </span>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Cloud AI Engine</span>
            <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="text-sm font-bold text-slate-800 flex items-center gap-1.5 pt-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Groq Cloud Active</span>
          </div>
          <span className="text-[11px] text-slate-400 font-medium block truncate">
            {stats?.system_status?.llm_provider?.status === 'operational' ? 'Groq Llama-3.3-70B Online' : 'Groq API Configured'}
          </span>
        </div>

      </div>

      {/* Quick Action Panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Action 1: Upload Report */}
        <div className="bg-gradient-to-br from-brand-600 to-brand-800 rounded-3xl p-6 sm:p-8 text-white relative overflow-hidden shadow-lg shadow-brand-700/20 flex flex-col justify-between">
          <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-44 h-44 bg-white/10 rounded-full blur-2xl pointer-events-none"></div>
          <div className="space-y-3 relative z-10">
            <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-md flex items-center justify-center text-white">
              <UploadCloud className="w-5 h-5" />
            </div>
            <h3 className="text-xl font-bold">Interpret Laboratory Report</h3>
            <p className="text-brand-100 text-xs sm:text-sm leading-relaxed max-w-sm">
              Upload blood tests, metabolic panels, or scanned pathology PDFs. 
              Extracts values, flags out-of-range biomarkers, and cites MedlinePlus references.
            </p>
          </div>
          <div className="pt-6 relative z-10">
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white text-brand-800 font-bold text-xs hover:bg-brand-50 transition shadow-sm"
            >
              <span>Upload Document</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* Action 2: Analyze X-ray */}
        <div className="bg-gradient-to-br from-teal-700 to-slate-900 rounded-3xl p-6 sm:p-8 text-white relative overflow-hidden shadow-lg shadow-teal-800/20 flex flex-col justify-between">
          <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-44 h-44 bg-teal-400/10 rounded-full blur-2xl pointer-events-none"></div>
          <div className="space-y-3 relative z-10">
            <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-md flex items-center justify-center text-white">
              <Activity className="w-5 h-5" />
            </div>
            <h3 className="text-xl font-bold">Chest Radiograph Interpretation</h3>
            <p className="text-teal-100 text-xs sm:text-sm leading-relaxed max-w-sm">
              Analyze chest radiographs with cloud-hosted inference models across 14 thoracic 
              pathologies including Cardiomegaly, Pneumonia, and Pleural Effusion.
            </p>
          </div>
          <div className="pt-6 relative z-10">
            <Link
              href="/xray"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-teal-400 text-slate-950 font-bold text-xs hover:bg-teal-300 transition shadow-sm"
            >
              <span>Analyze Radiograph</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

      </div>

      {/* Recent Studies & Reports */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-brand-600" />
            <h3 className="font-bold text-slate-900 text-sm">Recent Analyses &amp; Diagnostic Studies</h3>
          </div>
          <Link href="/history" className="text-xs font-semibold text-brand-600 hover:underline">
            View All History →
          </Link>
        </div>

        <div className="divide-y divide-slate-100">
          {stats?.recent_reports?.length > 0 || stats?.recent_xrays?.length > 0 ? (
            <>
              {stats?.recent_reports?.map((rep: any) => (
                <div key={`rep-${rep.id}`} className="px-6 py-4 flex items-center justify-between hover:bg-slate-50/80 transition">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-blue-50 text-brand-600 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-slate-900">{rep.title}</h4>
                      <p className="text-xs text-slate-400">{rep.original_filename} • {new Date(rep.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {rep.status}
                    </span>
                    <Link
                      href={`/analysis/${rep.id}`}
                      className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition"
                    >
                      View
                    </Link>
                    <a
                      href={api.getReportPdfUrl(rep.id)}
                      download
                      className="p-1.5 rounded-lg text-slate-400 hover:text-brand-600 hover:bg-brand-50 transition"
                      title="Download PDF"
                    >
                      <Download className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}

              {stats?.recent_xrays?.map((x: any) => (
                <div key={`xray-${x.id}`} className="px-6 py-4 flex items-center justify-between hover:bg-slate-50/80 transition">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center flex-shrink-0">
                      <Activity className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-slate-900">Chest Radiograph ({x.original_filename})</h4>
                      <p className="text-xs text-slate-400">Hosted Imaging • {new Date(x.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-teal-50 text-teal-700 border border-teal-200">
                      Radiology
                    </span>
                    <Link
                      href={`/xray/${x.id}`}
                      className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition"
                    >
                      View
                    </Link>
                    <a
                      href={api.getXrayPdfUrl(x.id)}
                      download
                      className="p-1.5 rounded-lg text-slate-400 hover:text-teal-600 hover:bg-teal-50 transition"
                      title="Download PDF"
                    >
                      <Download className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}
            </>
          ) : (
            <div className="px-6 py-12 text-center space-y-3">
              <UploadCloud className="w-8 h-8 text-slate-300 mx-auto" />
              <p className="text-sm text-slate-500 font-medium">No medical documents analyzed yet.</p>
              <Link
                href="/upload"
                className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-600 hover:underline"
              >
                Upload your first report or X-ray study →
              </Link>
            </div>
          )}
        </div>
      </div>

    </div>
  );
}


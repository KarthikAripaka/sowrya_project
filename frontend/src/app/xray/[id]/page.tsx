"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Activity, 
  ArrowLeft, 
  Download, 
  ShieldAlert, 
  CheckCircle2, 
  AlertCircle,
  ExternalLink,
  Cpu
} from 'lucide-react';
import { api } from '@/lib/api';

export default function XrayDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [xray, setXray] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const fetchStudy = async () => {
      try {
        const data = await api.getXray(id);
        setXray(data);
      } catch (err: any) {
        setError(err.message || "Failed to load X-ray study.");
      } finally {
        setLoading(false);
      }
    };
    fetchStudy();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-3">
        <div className="w-8 h-8 border-3 border-teal-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-xs text-slate-500 font-medium">Loading radiograph study...</p>
      </div>
    );
  }

  if (error || !xray) {
    return (
      <div className="max-w-2xl mx-auto py-16 px-4 text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-rose-500 mx-auto" />
        <h2 className="text-xl font-bold text-slate-900">Study Not Found</h2>
        <p className="text-xs text-slate-500">{error || "The requested radiograph study could not be found."}</p>
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-teal-600 text-white text-xs font-semibold"
        >
          <ArrowLeft className="w-4 h-4" /> Return to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-500 font-medium mb-1">
            <Link href="/dashboard" className="hover:text-teal-600">Dashboard</Link>
            <span>/</span>
            <Link href="/history" className="hover:text-teal-600">History</Link>
            <span>/</span>
            <span className="text-slate-800 font-semibold">Study #{xray.id}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Chest Radiograph Study</span>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-teal-100 text-teal-800 border border-teal-200">
              Completed
            </span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            File: <span className="font-semibold text-slate-700">{xray.original_filename}</span> • {new Date(xray.created_at).toLocaleString()}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={api.getXrayPdfUrl(xray.id)}
            download
            className="px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-sm flex items-center gap-2 transition"
          >
            <Download className="w-4 h-4" />
            <span>Download X-ray PDF</span>
          </a>
        </div>
      </div>

      {/* Medical Safety Banner */}
      <div className="bg-amber-50/70 border border-amber-200/80 rounded-2xl p-4 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-xs text-amber-900 space-y-0.5">
          <span className="font-bold uppercase tracking-wider block">RESEARCH ONLY: NOT A CONFIRMED RADIOLOGY DIAGNOSIS</span>
          <p className="text-amber-800 leading-relaxed">
            Cloud imaging model outputs provide statistical research observations. A board-certified radiologist must interpret all radiographs.
          </p>
        </div>
      </div>

      {/* Findings Summary */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wider flex items-center gap-2">
          <Activity className="w-4 h-4 text-teal-600" />
          <span>Preliminary Radiographic Findings</span>
        </h3>
        <p className="text-sm font-semibold text-slate-800 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-200">
          {xray.preliminary_findings}
        </p>
      </div>

      {/* Pathology Scores Table */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h4 className="font-bold text-slate-900 text-sm">
            Evaluated Thoracic Pathologies ({xray.observations_json?.length || 14} Classes)
          </h4>
          <span className="text-xs text-slate-400 font-mono">DenseNet-121</span>
        </div>

        <div className="divide-y divide-slate-100">
          {xray.observations_json?.map((obs: any, i: number) => {
            const score = obs.score ?? 0;
            const level = obs.confidence_level || 'Low';
            const barColor = level === 'High' ? 'bg-rose-500' : level === 'Moderate' ? 'bg-amber-500' : 'bg-emerald-500';
            const badgeColor = level === 'High' ? 'bg-rose-50 text-rose-700 border-rose-200' : level === 'Moderate' ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-emerald-50 text-emerald-700 border-emerald-200';

            return (
              <div key={i} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/80 transition">
                <div className="space-y-1 sm:max-w-sm">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-sm">{obs.pathology}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeColor}`}>
                      {level} Signal
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 leading-snug">{obs.explanation}</p>
                </div>

                <div className="flex items-center gap-3 flex-shrink-0 sm:w-48">
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${barColor}`}
                      style={{ width: `${Math.min(score * 100, 100)}%` }}
                    ></div>
                  </div>
                  <span className="font-mono text-xs font-bold text-slate-700 w-10 text-right">
                    {score.toFixed(2)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}


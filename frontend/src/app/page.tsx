"use client";

import React from 'react';
import Link from 'next/link';
import { 
  Activity, 
  FileText, 
  UploadCloud, 
  ShieldCheck, 
  CheckCircle2, 
  Search, 
  Cpu, 
  Database, 
  ArrowRight, 
  Layers, 
  Microscope, 
  FileCheck, 
  ExternalLink,
  Lock,
  ChevronRight,
  HelpCircle,
  AlertCircle
} from 'lucide-react';

export default function LandingPage() {
  const steps = [
    {
      num: "01",
      title: "Document Ingestion & Cloud OCR",
      desc: "Upload lab PDFs, scans, or radiographs. Cloud OCR & PyPDF extract digital text with strict numerical preservation and page traceability.",
      icon: UploadCloud,
    },
    {
      num: "02",
      title: "Medical Named Entity Recognition",
      desc: "Biomedical NER identifies biomarkers, numerical values, measurement units, diseases, symptoms, and compares against clinical reference intervals.",
      icon: Microscope,
    },
    {
      num: "03",
      title: "Biomedical Vector RAG Retrieval",
      desc: "PostgreSQL pgvector retrieves verified medical guidelines from MedlinePlus (NIH), PubMed, WHO, and RadiologyInfo.org without hallucinated citations.",
      icon: Database,
    },
    {
      num: "04",
      title: "Evidence-Grounded Synthesis",
      desc: "Groq Cloud API (Llama-3.3-70B) translates complex medical results into plain English explanations, doctor discussion points, and downloadable PDF reports with ultra-low latency.",
      icon: FileCheck,
    },
  ];

  const features = [
    {
      title: "Exact Numerical Value Preservation",
      desc: "Never rounds, alters, or invents laboratory values. Every extracted number is bound to its exact source page.",
      icon: CheckCircle2,
      tag: "Data Integrity"
    },
    {
      title: "Hosted Medical Imaging API",
      desc: "Cloud radiograph analysis across 14 chest pathologies with quality grading, sharpness metrics, and uncertainty scoring.",
      icon: Activity,
      tag: "Vision AI"
    },
    {
      title: "Clickable Peer-Reviewed Citations",
      desc: "Every explanation cites accredited medical organizations: MedlinePlus, PubMed, WHO, and RadiologyInfo.",
      icon: Search,
      tag: "Grounding"
    },
    {
      title: "100% Cloud-Native Performance",
      desc: "Powered by Groq's high-speed cloud inference, PostgreSQL pgvector, and cloud OCR. No GPU or model downloads needed.",
      icon: Lock,
      tag: "Cloud AI"
    },
    {
      title: "Doctor Discussion Points",
      desc: "Pre-generates actionable, personalized consultation questions so patients can have productive discussions with their doctors.",
      icon: HelpCircle,
      tag: "Patient Empowerment"
    },
    {
      title: "Automated Clinical PDF Export",
      desc: "Generates formatted, evidence-cited PDF summaries with ReportLab, including prominent medical disclaimers.",
      icon: FileText,
      tag: "Report Generation"
    }
  ];

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-32 bg-gradient-to-b from-white via-brand-50/30 to-slate-50 border-b border-slate-200/60">
        <div className="absolute inset-0 bg-[radial-gradient(#0284c7_1px,transparent_1px)] [background-size:24px_24px] opacity-10"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          
          <div className="text-center max-w-3xl mx-auto space-y-6">
            
            {/* Pill Announcement */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-50 border border-brand-200/80 text-brand-700 text-xs font-semibold shadow-sm">
              <span className="flex h-2 w-2 rounded-full bg-brand-500 animate-ping"></span>
              <span>Evidence-Based Medical Interpretation System</span>
              <span className="text-brand-400">•</span>
              <span className="text-teal-700 font-bold">Zero-Cost Academic Project</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15]">
              Understand Medical Reports &amp; X-rays with{' '}
              <span className="bg-gradient-to-r from-brand-600 via-teal-600 to-brand-700 bg-clip-text text-transparent">
                Evidence-Based AI
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-base sm:text-lg md:text-xl text-slate-600 font-normal leading-relaxed max-w-2xl mx-auto">
              Transform dense laboratory results and chest radiographs into transparent, 
              patient-friendly explanations grounded in peer-reviewed clinical knowledge—running 
              100% locally with zero external API fees.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <Link
                href="/upload"
                className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-sm shadow-md shadow-brand-600/30 flex items-center justify-center gap-2 group transition-all"
              >
                <UploadCloud className="w-4 h-4 group-hover:-translate-y-0.5 transition-transform" />
                <span>Upload Medical Report</span>
                <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
              </Link>
              
              <Link
                href="/xray"
                className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-sm shadow-md shadow-teal-600/30 flex items-center justify-center gap-2 group transition-all"
              >
                <Activity className="w-4 h-4 group-hover:-translate-y-0.5 transition-transform" />
                <span>Analyze Chest X-ray</span>
              </Link>

              <Link
                href="/dashboard"
                className="w-full sm:w-auto px-5 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-semibold text-sm border border-slate-300 shadow-sm flex items-center justify-center gap-2 transition"
              >
                <span>Live Dashboard</span>
              </Link>
            </div>

            {/* Credibility badges */}
            <div className="pt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-500 font-medium">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Cloud OCR Engine</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Hosted Medical Imaging</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Biomedical NER & RAG</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Groq Cloud Llama-3.3-70B</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Interactive Pipeline: How It Works */}
      <section className="py-20 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-brand-600 tracking-wider uppercase mb-2">
              End-to-End Processing
            </h2>
            <h3 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              How the Multi-Stage Medical AI Works
            </h3>
            <p className="text-slate-600 mt-3 text-sm">
              Each document passes through five traceable verification stages before patient synthesis.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
            {steps.map((s, idx) => {
              const Icon = s.icon;
              return (
                <div 
                  key={s.num} 
                  className="bg-slate-50 rounded-2xl p-6 border border-slate-200/80 hover:border-brand-300 hover:shadow-lg transition-all group relative flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-2xl font-black text-slate-300 group-hover:text-brand-500 transition-colors">
                        {s.num}
                      </span>
                      <div className="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-brand-600 shadow-sm group-hover:scale-110 transition-transform">
                        <Icon className="w-5 h-5" />
                      </div>
                    </div>
                    <h4 className="font-bold text-slate-900 text-base mb-2 group-hover:text-brand-700 transition-colors">
                      {s.title}
                    </h4>
                    <p className="text-slate-600 text-xs leading-relaxed">
                      {s.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

        </div>
      </section>

      {/* Core Features Grid */}
      <section className="py-20 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-teal-600 tracking-wider uppercase mb-2">
              Clinical Rigor &amp; Transparency
            </h2>
            <h3 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Built for Safety, Accuracy &amp; Understanding
            </h3>
            <p className="text-slate-600 mt-3 text-sm">
              Engineered with uncertainty-awareness, verifiable citations, and complete patient data isolation.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map((f, i) => {
              const Icon = f.icon;
              return (
                <div
                  key={i}
                  className="bg-white rounded-2xl p-6 border border-slate-200 hover:border-slate-300 shadow-sm hover:shadow-md transition-all space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="w-10 h-10 rounded-xl bg-brand-50 border border-brand-100 flex items-center justify-center text-brand-600">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
                      {f.tag}
                    </span>
                  </div>
                  <h4 className="font-bold text-slate-900 text-base">
                    {f.title}
                  </h4>
                  <p className="text-slate-600 text-xs leading-relaxed">
                    {f.desc}
                  </p>
                </div>
              );
            })}
          </div>

        </div>
      </section>

      {/* Medical Safety Disclaimer Callout */}
      <section className="py-16 bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600 mx-auto">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h3 className="text-2xl font-bold text-slate-900">
            Educational Purpose &amp; Physician Partnership
          </h3>
          <p className="text-slate-600 text-sm leading-relaxed max-w-2xl mx-auto">
            MediEvidence AI empowers patients to become informed partners in their healthcare. 
            AI algorithms cannot replace laboratory quality control or professional medical judgment. 
            Always review results with your licensed healthcare provider before making any clinical decisions.
          </p>
          <div className="pt-2">
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 text-brand-600 font-bold text-sm hover:underline"
            >
              <span>Get started by uploading a sample report</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

    </div>
  );
}


import React from 'react';
import Link from 'next/link';
import { Activity, ShieldCheck, Heart, Github, BookOpen, ExternalLink, Cloud } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 border-t border-slate-800 text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          
          {/* Col 1: Brand & Mission */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-teal-500 flex items-center justify-center text-white">
                <Activity className="w-4 h-4" />
              </div>
              <span className="font-bold text-white text-base">
                MediEvidence <span className="text-brand-400">AI</span>
              </span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed max-w-md">
              An evidence-based medical report and radiograph interpretation system. 
              Powered by ultra-fast Groq Cloud API (Llama-3.3-70B), Cloud OCR, 
              PostgreSQL pgvector, and Hosted Medical Imaging inference.
            </p>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="inline-flex items-center gap-1 text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2.5 py-0.5 rounded-full">
                <Cloud className="w-3.5 h-3.5" /> 100% Cloud AI (Groq Llama-3.3-70B)
              </span>
              <span>•</span>
              <span>No Local GPU Required</span>
            </div>
          </div>

          {/* Col 2: Core Modules */}
          <div>
            <h4 className="text-white font-semibold text-xs tracking-wider uppercase mb-3">
              AI Engines
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/upload" className="hover:text-white transition">
                  Cloud OCR & Biomedical NER
                </Link>
              </li>
              <li>
                <Link href="/xray" className="hover:text-white transition">
                  Hosted Medical Imaging API
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="hover:text-white transition">
                  pgvector Evidence-Based RAG
                </Link>
              </li>
              <li>
                <Link href="/history" className="hover:text-white transition">
                  Evidence Citation Tracking
                </Link>
              </li>
              <li>
                <Link href="/settings" className="hover:text-white transition">
                  Groq Cloud LLM Provider
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Peer-Reviewed Sources */}
          <div>
            <h4 className="text-white font-semibold text-xs tracking-wider uppercase mb-3">
              Knowledge Sources
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="https://medlineplus.gov" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white transition">
                  MedlinePlus (NIH) <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://pubmed.ncbi.nlm.nih.gov" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white transition">
                  PubMed Clinical Guidelines <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://www.who.int" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white transition">
                  World Health Organization <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://www.radiologyinfo.org" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white transition">
                  RadiologyInfo.org (RSNA) <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Disclaimer */}
        <div className="pt-6 border-t border-slate-800 text-[11px] text-slate-400 space-y-2">
          <p className="font-semibold text-slate-300">
            MANDATORY MEDICAL SAFETY DISCLAIMER:
          </p>
          <p className="leading-relaxed">
            This application provides AI-assisted educational explanations of medical reports and diagnostic images. It does not provide a medical diagnosis or replace consultation with a qualified healthcare professional. AI-generated results may contain errors and must be reviewed by an appropriately qualified medical professional. Never alter prescribed treatments without professional medical oversight.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-between pt-4 text-slate-400">
            <span>© 2026 MediEvidence AI. Academic & Research Open-Source Project.</span>
            <div className="flex items-center gap-4 mt-2 sm:mt-0">
              <Link href="/settings" className="hover:text-slate-300">Privacy & Cloud Settings</Link>
              <span>•</span>
              <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-slate-300">Backend API Docs</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

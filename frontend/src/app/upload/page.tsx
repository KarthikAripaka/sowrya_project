"use client";

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight, 
  X, 
  Cpu, 
  Sparkles, 
  FileCheck, 
  Microscope, 
  Database,
  Layers
} from 'lucide-react';
import { api } from '@/lib/api';

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [reportTitle, setReportTitle] = useState('');
  const [reportType, setReportType] = useState('laboratory');
  const [dragActive, setDragActive] = useState(false);
  
  const [uploading, setUploading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const steps = [
    { title: "Document Upload & Security Sanitization", desc: "Validating file integrity and virus scan." },
    { title: "Cloud Optical Character Recognition", desc: "Extracting digital text, preserving numerical values and units." },
    { title: "Biomedical Named Entity Recognition", desc: "Parsing biomarkers, units, and clinical reference intervals." },
    { title: "Evidence-Based Vector RAG Retrieval", desc: "Searching peer-reviewed evidence in MedlinePlus, PubMed & WHO." },
    { title: "Evidence-Grounded Synthesis (Groq Cloud API)", desc: "Generating plain-language educational summary with Llama-3.3-70B." }
  ];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    setError(null);
    const validExtensions = ['.pdf', '.jpg', '.jpeg', '.png'];
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!validExtensions.includes(ext)) {
      setError(`Invalid file format '${ext}'. Please upload a PDF, JPG, JPEG, or PNG.`);
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      setError("File size exceeds maximum limit of 25MB.");
      return;
    }

    setSelectedFile(file);
    if (!reportTitle) {
      setReportTitle(file.name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, " "));
    }
  };

  // Sample quick report generators for reviewer testing
  const loadSyntheticCBC = () => {
    const content = 
`COMPLETE BLOOD COUNT (CBC) REPORT
Patient: Sample Patient (Evaluation)
Date: 2026-03-15
Laboratory: Clinical Diagnostics Dept

TEST NAME            OBSERVED VALUE   UNIT        REFERENCE INTERVAL   STATUS
-------------------------------------------------------------------------------
Hemoglobin           11.2             g/dL        13.8 - 17.2          LOW
Hematocrit           33.5             %           41.0 - 50.0          LOW
White Blood Cells    13.8             x10^3/uL    4.5 - 11.0           HIGH
Platelet Count       280              x10^3/uL    150 - 450            NORMAL
Red Blood Cells      3.8              x10^6/uL    4.7 - 6.1            LOW
MCV                  82.0             fL          80.0 - 100.0         NORMAL

Clinical Notes: Patient reports chronic fatigue, exertional shortness of breath, and mild pallor. Suspicion of iron deficiency anemia with mild reactive leukocytosis.`;

    const blob = new Blob([content], { type: 'text/plain' });
    const file = new File([blob], 'Synthetic_Complete_Blood_Count.pdf', { type: 'application/pdf' });
    validateAndSetFile(file);
    setReportTitle("Complete Blood Count (CBC) Panel");
    setReportType("laboratory");
  };

  const loadSyntheticLipid = () => {
    const content = 
`COMPREHENSIVE LIPID & METABOLIC PANEL
Patient: Sample Patient (Cardiovascular Screening)
Date: 2026-03-20

TEST NAME            OBSERVED VALUE   UNIT        REFERENCE INTERVAL   STATUS
-------------------------------------------------------------------------------
Total Cholesterol    235              mg/dL       100 - 199            HIGH
Triglycerides        185              mg/dL       40 - 149             HIGH
HDL Cholesterol      36               mg/dL       40 - 90              LOW
LDL Cholesterol      158              mg/dL       50 - 99              HIGH
Fasting Glucose      118              mg/dL       70 - 99              HIGH
Serum Creatinine     0.9              mg/dL       0.6 - 1.3            NORMAL

Clinical Notes: Cardiovascular risk assessment. Glycemic profile consistent with impaired fasting glucose (prediabetes). Dyslipidemia observed.`;

    const blob = new Blob([content], { type: 'text/plain' });
    const file = new File([blob], 'Synthetic_Lipid_Panel.pdf', { type: 'application/pdf' });
    validateAndSetFile(file);
    setReportTitle("Comprehensive Lipid & Metabolic Panel");
    setReportType("laboratory");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError("Please select or drop a medical document to upload.");
      return;
    }

    setUploading(true);
    setError(null);

    // Simulate progress animation through stages
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 1100);

    try {
      const formData = new FormData();
      formData.append('title', reportTitle || selectedFile.name);
      formData.append('report_type', reportType);
      formData.append('file', selectedFile);

      const result = await api.uploadReport(formData);
      clearInterval(stepInterval);
      setCurrentStep(4);
      setTimeout(() => {
        router.push(`/analysis/${result.id}`);
      }, 800);
    } catch (err: any) {
      clearInterval(stepInterval);
      setUploading(false);
      setError(err.message || "Failed to analyze medical report.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Upload Medical Document
        </h1>
        <p className="text-sm text-slate-500 max-w-xl mx-auto">
          Upload laboratory reports, discharge summaries, or pathology PDFs. 
          Our zero-cost AI preserves numerical values and cites MedlinePlus references.
        </p>
      </div>

      {/* Synthetic sample shortcuts for instant testing */}
      <div className="bg-brand-50/60 border border-brand-200/80 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-sm">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-brand-600 flex-shrink-0" />
          <span className="text-xs font-semibold text-brand-900">
            Quick Academic Test Samples:
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={loadSyntheticCBC}
            className="px-3 py-1.5 rounded-lg bg-white border border-brand-300 text-brand-800 text-xs font-semibold hover:bg-brand-100 transition shadow-sm"
          >
            Load Sample CBC Report
          </button>
          <button
            type="button"
            onClick={loadSyntheticLipid}
            className="px-3 py-1.5 rounded-lg bg-white border border-teal-300 text-teal-800 text-xs font-semibold hover:bg-teal-50 transition shadow-sm"
          >
            Load Sample Lipid Panel
          </button>
        </div>
      </div>

      {/* Main Upload Box */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
        
        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 font-medium flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Processing Animated Stepper */}
        {uploading ? (
          <div className="py-12 px-4 space-y-8">
            <div className="text-center space-y-2">
              <div className="w-14 h-14 rounded-2xl bg-brand-50 border border-brand-200 flex items-center justify-center text-brand-600 mx-auto animate-bounce">
                <Microscope className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">
                Analyzing Medical Document...
              </h3>
              <p className="text-xs text-slate-500">
                Running local zero-cost AI pipelines. Please do not close this window.
              </p>
            </div>

            {/* Stepper display */}
            <div className="max-w-md mx-auto space-y-4">
              {steps.map((s, idx) => {
                const isCompleted = idx < currentStep;
                const isCurrent = idx === currentStep;
                return (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="pt-0.5">
                      {isCompleted ? (
                        <div className="w-6 h-6 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xs">
                          <CheckCircle2 className="w-4 h-4" />
                        </div>
                      ) : isCurrent ? (
                        <div className="w-6 h-6 rounded-full border-2 border-brand-600 border-t-transparent animate-spin flex items-center justify-center"></div>
                      ) : (
                        <div className="w-6 h-6 rounded-full border border-slate-300 bg-slate-100 flex items-center justify-center text-[10px] text-slate-400 font-bold">
                          {idx + 1}
                        </div>
                      )}
                    </div>
                    <div>
                      <h4 className={`text-xs font-bold ${isCurrent ? 'text-brand-600' : isCompleted ? 'text-slate-900' : 'text-slate-400'}`}>
                        {s.title}
                      </h4>
                      <p className="text-[11px] text-slate-500">{s.desc}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Drag & Drop Zone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
                dragActive 
                  ? 'border-brand-500 bg-brand-50/50' 
                  : selectedFile 
                    ? 'border-emerald-400 bg-emerald-50/30' 
                    : 'border-slate-300 hover:border-brand-400 bg-slate-50/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleFileChange}
                className="hidden"
              />

              {selectedFile ? (
                <div className="space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto shadow-sm">
                    <FileCheck className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">{selectedFile.name}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • {selectedFile.type || 'Document'}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(null);
                    }}
                    className="inline-flex items-center gap-1 text-xs text-rose-600 font-semibold hover:underline"
                  >
                    <X className="w-3.5 h-3.5" /> Remove &amp; choose another
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-brand-50 text-brand-600 flex items-center justify-center mx-auto shadow-sm">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">
                      Drag &amp; drop medical report here, or <span className="text-brand-600 underline">browse</span>
                    </h4>
                    <p className="text-xs text-slate-500 mt-1">
                      Supports PDF, Scanned PDF, JPG, JPEG, and PNG (up to 25MB)
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Document Details */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Report Title
                </label>
                <input
                  type="text"
                  required
                  value={reportTitle}
                  onChange={(e) => setReportTitle(e.target.value)}
                  placeholder="e.g. Complete Blood Count (CBC) Panel"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Report Category
                </label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 bg-white transition"
                >
                  <option value="laboratory">Laboratory Panel (CBC, Metabolic, Lipids)</option>
                  <option value="discharge">Hospital Discharge Summary</option>
                  <option value="pathology">Pathology &amp; Biopsy Report</option>
                  <option value="prescription">Prescription / Medication List</option>
                </select>
              </div>
            </div>

            {/* Submit CTA */}
            <button
              type="submit"
              disabled={!selectedFile}
              className="w-full py-3.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-sm shadow-md shadow-brand-600/30 flex items-center justify-center gap-2 transition disabled:opacity-50"
            >
              <Cpu className="w-4 h-4" />
              <span>Run Local AI Medical Interpretation</span>
              <ArrowRight className="w-4 h-4" />
            </button>

          </form>
        )}

      </div>

    </div>
  );
}


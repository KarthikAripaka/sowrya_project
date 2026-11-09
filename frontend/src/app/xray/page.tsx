"use client";

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Activity, 
  UploadCloud, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight, 
  ShieldAlert, 
  Microscope, 
  Sparkles, 
  Download, 
  ExternalLink,
  Cpu,
  Layers,
  FileCheck
} from 'lucide-react';
import { api } from '@/lib/api';

export default function XrayPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
      setResult(null);
    }
  };

  // Generate a valid synthetic Chest X-ray PNG in canvas for instant testing
  const generateSyntheticChestXray = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Draw dark thoracic background
    ctx.fillStyle = '#111827';
    ctx.fillRect(0, 0, 512, 512);

    // Rib cage arches
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 6;
    for (let y = 100; y < 420; y += 45) {
      ctx.beginPath();
      ctx.ellipse(256, y, 180, 40, 0, 0, Math.PI);
      ctx.stroke();
    }

    // Spine / vertebrae column
    ctx.fillStyle = '#4b5563';
    ctx.fillRect(246, 50, 20, 380);

    // Lung fields (radiolucent dark areas)
    ctx.fillStyle = '#030712';
    // Left lung
    ctx.beginPath();
    ctx.ellipse(170, 240, 65, 130, -0.1, 0, Math.PI * 2);
    ctx.fill();
    // Right lung
    ctx.beginPath();
    ctx.ellipse(342, 240, 65, 130, 0.1, 0, Math.PI * 2);
    ctx.fill();

    // Cardiac silhouette (enlarged heart / cardiomegaly finding for educational detection)
    ctx.fillStyle = '#4b5563';
    ctx.beginPath();
    ctx.ellipse(280, 290, 85, 70, 0.35, 0, Math.PI * 2);
    ctx.fill();

    // Hemidiaphragm curves
    ctx.fillStyle = '#374151';
    ctx.beginPath();
    ctx.arc(160, 420, 90, Math.PI, 0, false);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(350, 430, 90, Math.PI, 0, false);
    ctx.fill();

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'Sample_Chest_Radiograph_PA.png', { type: 'image/png' });
        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(file));
        setError(null);
        setResult(null);
      }
    }, 'image/png');
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError("Please select or generate a chest radiograph image.");
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const res = await api.uploadXray(formData);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "X-ray analysis failed.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Chest Radiograph Interpretation</span>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-teal-100 text-teal-800 border border-teal-200">
              Hosted Medical Imaging API
            </span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Cloud deep-learning feature analysis across 14 thoracic pathologies
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={generateSyntheticChestXray}
            className="px-3.5 py-2 rounded-xl bg-teal-50 border border-teal-200 text-teal-800 text-xs font-bold hover:bg-teal-100 transition shadow-sm flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-teal-600" />
            <span>Load Sample Chest X-ray</span>
          </button>
        </div>
      </div>

      {/* Medical Safety Banner */}
      <div className="bg-amber-50/70 border border-amber-200/80 rounded-2xl p-4 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-xs text-amber-900 space-y-0.5">
          <span className="font-bold uppercase tracking-wider block">RESEARCH OBSERVATION ONLY – NOT A CONFIRMED RADIOLOGY DIAGNOSIS</span>
          <p className="text-amber-800 leading-relaxed">
            Cloud imaging model activations reflect statistical research feature detection, not certified physician readings. 
            All radiographic findings must be formally evaluated by a board-certified radiologist.
          </p>
        </div>
      </div>

      {/* Main Grid: Upload & Preview on Left, Results on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Image Viewer / Upload */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide flex items-center gap-2">
              <Microscope className="w-4 h-4 text-teal-600" />
              <span>Radiograph Input</span>
            </h3>

            {/* Image Preview Box */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className="aspect-square bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 flex items-center justify-center relative cursor-pointer group shadow-inner"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />

              {previewUrl ? (
                <div className="w-full h-full relative flex items-center justify-center p-2">
                  <img
                    src={previewUrl}
                    alt="Radiograph Preview"
                    className="max-h-full max-w-full object-contain rounded-lg"
                  />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold">
                    Click to change radiograph
                  </div>
                </div>
              ) : (
                <div className="text-center p-6 space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-slate-900 text-teal-400 border border-slate-800 flex items-center justify-center mx-auto">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-200">
                      Upload Chest X-ray Image
                    </h4>
                    <p className="text-[11px] text-slate-400 mt-1">
                      Supports PNG, JPG, JPEG, and DICOM
                    </p>
                  </div>
                </div>
              )}
            </div>

            {selectedFile && (
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 flex items-center justify-between">
                <span className="font-semibold truncate max-w-[200px]">{selectedFile.name}</span>
                <span className="text-slate-400">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
              </div>
            )}

            <button
              type="button"
              onClick={handleAnalyze}
              disabled={!selectedFile || analyzing}
              className="w-full py-3.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-md shadow-teal-600/30 flex items-center justify-center gap-2 transition disabled:opacity-50"
            >
              {analyzing ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  Running Cloud Imaging Inference...
                </span>
              ) : (
                <>
                  <Cpu className="w-4 h-4" />
                  <span>Execute Thoracic Analysis</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: AI Analysis Observations */}
        <div className="lg:col-span-7 space-y-6">
          {result ? (
            <div className="space-y-6">
              
              {/* Findings Overview */}
              <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-teal-600" />
                    <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wider">
                      Preliminary Radiographic Observations
                    </h3>
                  </div>
                  <a
                    href={api.getXrayPdfUrl(result.id)}
                    download
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-50 border border-teal-200 text-teal-800 text-xs font-bold hover:bg-teal-100 transition shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download PDF</span>
                  </a>
                </div>

                <p className="text-sm font-semibold text-slate-800 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-200/80">
                  {result.preliminary_findings}
                </p>

                {/* Technical Quality Metadata */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1">
                  <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Image Quality</span>
                    <span className="font-bold text-slate-800">{result.image_quality}</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Anatomy</span>
                    <span className="font-bold text-slate-800">{result.anatomical_region}</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Model</span>
                    <span className="font-bold text-slate-800 truncate block">{result.model_name || "Hosted Imaging API"}</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Architecture</span>
                    <span className="font-bold text-slate-800">Cloud Inference</span>
                  </div>
                </div>
              </div>

              {/* Pathology Finding Activations Table */}
              <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
                  <h4 className="font-bold text-slate-900 text-sm">
                    Evaluated Thoracic Pathologies (14 Classes)
                  </h4>
                  <span className="text-xs text-slate-400 font-mono">
                    Threshold: ≥ 0.40 Elevated
                  </span>
                </div>

                <div className="divide-y divide-slate-100">
                  {(!result.observations_json || result.observations_json.length === 0) ? (
                    <div className="p-8 text-center space-y-3">
                      <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-200">
                        <ShieldAlert className="w-6 h-6" />
                      </div>
                      <div className="space-y-1 max-w-md mx-auto">
                        <h5 className="font-bold text-slate-800 text-sm">Hosted Medical Imaging API Awaiting Configuration</h5>
                        <p className="text-xs text-slate-500 leading-relaxed">
                          Under medical safety rules, this system never fabricates findings or generates simulated pathology scores. Image validation and quality checks succeeded. To enable cloud inference, configure <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-700">IMAGING_API_URL</code> in backend environment variables.
                        </p>
                      </div>
                    </div>
                  ) : (
                    result.observations_json.map((obs: any, i: number) => {
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

                        {/* Visual Activation Bar */}
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
                  }))}
                </div>
              </div>

              {/* Research Model Limitations */}
              <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200 text-xs text-slate-600 space-y-2">
                <h5 className="font-bold text-slate-800 uppercase tracking-wide text-[11px]">
                  Documented Technical Limitations
                </h5>
                <p className="leading-relaxed whitespace-pre-line text-slate-500">
                  {result.limitations_text || "Model activations are uncalibrated feature activations. Clinical radiologist interpretation required."}
                </p>
              </div>

            </div>
          ) : (
            <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-12 text-center space-y-4">
              <div className="w-16 h-16 rounded-3xl bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-600 mx-auto">
                <Activity className="w-8 h-8" />
              </div>
              <div className="space-y-1 max-w-sm mx-auto">
                <h3 className="text-base font-bold text-slate-900">Awaiting Radiograph Input</h3>
                <p className="text-xs text-slate-500">
                  Upload an X-ray or click <strong>'Load Sample Chest X-ray'</strong> above to trigger cloud evaluation.
                </p>
              </div>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}


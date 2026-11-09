"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  History, 
  FileText, 
  Activity, 
  Search, 
  Download, 
  Trash2, 
  Filter, 
  Calendar,
  ExternalLink,
  Plus
} from 'lucide-react';
import { api } from '@/lib/api';

export default function HistoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getHistory(searchTerm, filterType);
      setItems(data);
    } catch (err) {
      console.error("History fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [filterType]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchHistory();
  };

  const handleDelete = async (type: 'report' | 'xray', id: number) => {
    if (!confirm("Are you sure you want to permanently delete this analysis record?")) return;
    setDeletingId(`${type}-${id}`);
    try {
      await api.deleteHistoryItem(type, id);
      setItems((prev) => prev.filter((item) => !(item.type === type && item.id === id)));
    } catch (err: any) {
      alert("Delete failed: " + err.message);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <History className="w-6 h-6 text-brand-600" />
            <span>Analysis History &amp; Studies</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Search, filter, review, and download PDF summaries of past analyses
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/upload"
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs shadow-sm flex items-center gap-1.5 transition"
          >
            <Plus className="w-4 h-4" />
            <span>New Analysis</span>
          </Link>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        
        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by report title, biomarker, or filename..."
            className="w-full pl-10 pr-20 py-2 rounded-xl border border-slate-300 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition"
          />
          <button
            type="submit"
            className="absolute right-1.5 top-1 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition"
          >
            Search
          </button>
        </form>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-xl text-xs font-semibold self-start sm:self-auto">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3 py-1.5 rounded-lg transition ${
              filterType === 'all' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            All Studies
          </button>
          <button
            onClick={() => setFilterType('laboratory')}
            className={`px-3 py-1.5 rounded-lg transition ${
              filterType === 'laboratory' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Lab Reports
          </button>
          <button
            onClick={() => setFilterType('xray')}
            className={`px-3 py-1.5 rounded-lg transition ${
              filterType === 'xray' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Chest Radiographs
          </button>
        </div>

      </div>

      {/* History Items List */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="py-16 text-center space-y-2">
            <div className="w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-xs text-slate-400 font-medium">Retrieving analysis history...</p>
          </div>
        ) : items.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {items.map((item) => {
              const isXray = item.type === 'xray';
              const targetUrl = isXray ? `/xray/${item.id}` : `/analysis/${item.id}`;
              const pdfUrl = isXray ? api.getXrayPdfUrl(item.id) : api.getReportPdfUrl(item.id);

              return (
                <div key={`${item.type}-${item.id}`} className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50/80 transition">
                  <div className="flex items-start gap-3">
                    <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 mt-0.5 ${
                      isXray ? 'bg-teal-50 text-teal-600' : 'bg-blue-50 text-brand-600'
                    }`}>
                      {isXray ? <Activity className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Link href={targetUrl} className="font-bold text-slate-900 text-sm hover:text-brand-600 transition">
                          {item.title}
                        </Link>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                          isXray ? 'bg-teal-50 text-teal-700 border-teal-200' : 'bg-blue-50 text-brand-700 border-blue-200'
                        }`}>
                          {item.category || item.type}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 line-clamp-2 max-w-2xl">
                        {item.summary || "Analysis completed successfully."}
                      </p>
                      <div className="flex items-center gap-3 text-[11px] text-slate-400 font-medium pt-0.5">
                        <span>File: {item.filename}</span>
                        <span>•</span>
                        <span>{new Date(item.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 self-end md:self-auto flex-shrink-0">
                    <Link
                      href={targetUrl}
                      className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition"
                    >
                      View Analysis
                    </Link>
                    
                    <a
                      href={pdfUrl}
                      download
                      className="p-2 rounded-lg text-slate-400 hover:text-brand-600 hover:bg-brand-50 transition"
                      title="Download PDF"
                    >
                      <Download className="w-4 h-4" />
                    </a>

                    <button
                      onClick={() => handleDelete(item.type, item.id)}
                      disabled={deletingId === `${item.type}-${item.id}`}
                      className="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
                      title="Delete Record"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="py-16 text-center space-y-3">
            <History className="w-10 h-10 text-slate-300 mx-auto" />
            <h4 className="text-sm font-bold text-slate-800">No records found</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No matching medical reports or radiographs found. Upload a report to begin analysis.
            </p>
            <div className="pt-2">
              <Link
                href="/upload"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-brand-600 text-white text-xs font-semibold shadow-sm"
              >
                Upload Medical Report
              </Link>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}


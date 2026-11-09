"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { 
  Activity, 
  FileText, 
  UploadCloud, 
  History, 
  Settings, 
  LogOut, 
  LogIn, 
  Menu, 
  X, 
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { api, getStoredUser, clearAuthToken } from '@/lib/api';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    setUser(getStoredUser());
  }, [pathname]);

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
    router.push('/login');
  };

  const navLinks = [
    { name: 'Dashboard', href: '/dashboard', icon: Activity },
    { name: 'Upload Report', href: '/upload', icon: UploadCloud },
    { name: 'Chest X-ray', href: '/xray', icon: FileText },
    { name: 'History', href: '/history', icon: History },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-700 via-brand-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition-transform">
              <Activity className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div>
              <span className="font-bold text-slate-900 tracking-tight text-lg flex items-center gap-1.5">
                MediEvidence <span className="text-brand-600 font-extrabold">AI</span>
              </span>
              <span className="hidden sm:block text-[10px] text-slate-500 font-medium tracking-wide uppercase">
                Evidence-Based Clinical AI
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href || pathname.startsWith(`${link.href}/`);
              return (
                <Link
                  key={link.name}
                  href={link.href}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-brand-50 text-brand-700'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-slate-400'}`} />
                  {link.name}
                </Link>
              );
            })}
          </nav>

          {/* Right Status & Instant Free Actions */}
          <div className="hidden sm:flex items-center gap-3">
            {/* Groq multi-key pool badge */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200/80 text-[11px] font-semibold text-emerald-800">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Groq Cloud (Failover Active)</span>
            </div>

            <Link
              href="/upload"
              className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-brand-600 hover:bg-brand-700 text-white shadow-sm shadow-brand-600/30 transition flex items-center gap-1.5"
            >
              <UploadCloud className="w-3.5 h-3.5" />
              <span>Instant Analyze</span>
            </Link>

            <Link
              href="/settings"
              className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition"
              title="Cloud Settings & Data Privacy"
            >
              <Settings className="w-4 h-4" />
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:bg-slate-100"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.name}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-base font-medium ${
                  isActive ? 'bg-brand-50 text-brand-700' : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <Icon className="w-5 h-5 text-slate-400" />
                {link.name}
              </Link>
            );
          })}
          <div className="pt-3 border-t border-slate-200 flex flex-col gap-2">
            {user ? (
              <button
                onClick={() => {
                  handleLogout();
                  setMobileMenuOpen(false);
                }}
                className="flex items-center gap-2 px-3 py-2 text-rose-600 font-medium"
              >
                <LogOut className="w-5 h-5" />
                Sign Out ({user.email})
              </button>
            ) : (
              <Link
                href="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center justify-center py-2.5 rounded-lg bg-brand-600 text-white font-semibold"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      )}
    </header>
  );
}


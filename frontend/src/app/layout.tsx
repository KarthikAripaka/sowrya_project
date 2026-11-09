import './globals.css';
import type { Metadata } from 'next';
import Navbar from '@/components/common/Navbar';
import DisclaimerBanner from '@/components/common/DisclaimerBanner';
import Footer from '@/components/common/Footer';

export const metadata: Metadata = {
  title: 'MediEvidence AI | Evidence-Based Medical Report & X-ray Interpretation',
  description: 'AI-assisted medical report interpretation and chest radiograph analysis powered by local Vision AI, BioBERT NER, and RAG.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="flex min-h-full flex-col bg-slate-50 text-slate-900 selection:bg-brand-500 selection:text-white">
        <DisclaimerBanner />
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}


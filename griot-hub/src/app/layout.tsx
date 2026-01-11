import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Griot Hub',
  description: 'Data contract management and monitoring - Open Data Contract Standard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-50`}>
        <div className="min-h-screen flex flex-col">
          <header className="bg-white border-b border-slate-200">
            <nav className="max-w-7xl mx-auto px-6">
              <div className="flex items-center justify-between h-16">
                {/* Logo & Primary Nav */}
                <div className="flex items-center gap-8">
                  <a href="/" className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold">G</span>
                    </div>
                    <span className="text-xl font-bold text-slate-800">Griot Hub</span>
                  </a>

                  {/* Primary Navigation */}
                  <div className="hidden md:flex items-center gap-1">
                    <a
                      href="/contracts"
                      className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                      Data Contracts
                    </a>
                    <a
                      href="/studio"
                      className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                      Studio
                    </a>
                    <a
                      href="/monitor"
                      className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                      Monitor
                    </a>

                    {/* Reports Dropdown */}
                    <div className="relative group">
                      <button className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors flex items-center gap-1">
                        Reports
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      <div className="absolute left-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-slate-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 py-2">
                        <a href="/audit" className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50">
                          Audit Dashboard
                        </a>
                        <a href="/finops" className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50">
                          FinOps Dashboard
                        </a>
                        <a href="/ai-readiness" className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50">
                          AI Readiness
                        </a>
                        <a href="/residency" className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50">
                          Residency Map
                        </a>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Actions */}
                <div className="flex items-center gap-4">
                  {/* Search */}
                  <div className="hidden md:flex items-center">
                    <div className="relative">
                      <svg
                        className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        />
                      </svg>
                      <input
                        type="text"
                        placeholder="Search contracts..."
                        className="w-64 pl-10 pr-4 py-2 text-sm bg-slate-100 border-none rounded-lg focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                      />
                    </div>
                  </div>

                  {/* New Contract Button */}
                  <a
                    href="/studio"
                    className="hidden md:inline-flex px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    New Contract
                  </a>

                  {/* Settings */}
                  <a
                    href="/settings"
                    className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                    </svg>
                  </a>
                </div>
              </div>
            </nav>
          </header>

          <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
            {children}
          </main>

          <footer className="bg-white border-t border-slate-200 px-6 py-4">
            <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-slate-500">
              <div>Griot Hub v1.0.0 • Open Data Contract Standard</div>
              <div className="flex gap-6">
                <a href="https://github.com/griot-project/griot" className="hover:text-slate-700">
                  Documentation
                </a>
                <a href="https://bitol.io/open-data-contract-standard/" className="hover:text-slate-700">
                  ODCS Specification
                </a>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}

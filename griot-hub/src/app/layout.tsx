import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Griot Hub',
  description: 'Data contract management and monitoring',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col">
          <header className="bg-white border-b border-gray-200 px-6 py-4">
            <nav className="max-w-7xl mx-auto flex items-center justify-between">
              <div className="flex items-center gap-8">
                <a href="/" className="text-xl font-bold text-primary-700">
                  Griot Hub
                </a>
                <div className="flex gap-6">
                  <a href="/contracts" className="text-gray-600 hover:text-gray-900">
                    Contracts
                  </a>
                  <a href="/studio" className="text-gray-600 hover:text-gray-900">
                    Studio
                  </a>
                  <a href="/monitor" className="text-gray-600 hover:text-gray-900">
                    Monitor
                  </a>
                  <div className="relative group">
                    <span className="text-gray-600 hover:text-gray-900 cursor-pointer">
                      Reports
                    </span>
                    <div className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                      <a href="/audit" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                        Audit Dashboard
                      </a>
                      <a href="/finops" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                        FinOps Dashboard
                      </a>
                      <a href="/ai-readiness" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                        AI Readiness
                      </a>
                      <a href="/residency" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                        Residency Map
                      </a>
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <a href="/settings" className="text-gray-600 hover:text-gray-900">
                  Settings
                </a>
              </div>
            </nav>
          </header>
          <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
            {children}
          </main>
          <footer className="border-t border-gray-200 px-6 py-4 text-center text-gray-500 text-sm">
            Griot Hub v0.1.0
          </footer>
        </div>
      </body>
    </html>
  );
}

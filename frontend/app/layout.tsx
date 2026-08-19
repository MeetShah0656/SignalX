import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SignalX - AI NIFTY Live Paper Trading System',
  description: 'Production-grade AI NIFTY 50 live paper-trading system and backtesting engine.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-white antialiased">
        {children}
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";
import { AuthProvider } from "@/lib/firebase/authContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import Link from 'next/link';

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "HackMap - Discover & Win Global Hackathons",
    template: "%s | HackMap"
  },
  description: "Find your next hackathon. HackMap aggregates global AI, Web3, and Open Source hackathons into one centralized, intelligent dashboard.",
  openGraph: {
    title: "HackMap - Discover Global Hackathons",
    description: "The intelligent hub for finding hackathons globally.",
    url: "https://hackmap.ai",
    siteName: "HackMap",
    images: [
      {
        url: "https://hackmap.ai/og-image.jpg",
        width: 1200,
        height: 630,
      }
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "HackMap",
    description: "Discover global hackathons effortlessly.",
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.variable}>
        <ThemeProvider attribute="data-theme" defaultTheme="system" enableSystem>
          <nav style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem 2rem', borderBottom: '1px solid var(--color-muted-sage)', background: 'var(--background)' }}>
            <div style={{ fontWeight: 'bold', fontSize: '1.25rem' }}>
              <Link href="/">HackMap</Link>
            </div>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <ThemeToggle />
              <Link href="/dashboard" style={{ color: 'var(--color-peach-glow)' }}>Dashboard</Link>
              <Link href="/login" style={{ color: 'var(--foreground)' }}>Login</Link>
            </div>
          </nav>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}

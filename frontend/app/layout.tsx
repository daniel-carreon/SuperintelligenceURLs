import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SuperintelligenceURLs - URL Shortener with Real-time Analytics",
  description: "Shorten URLs and track analytics in real-time. Free URL shortener with advanced device, geographic, and traffic source analytics.",
  keywords: ["url shortener", "link shortener", "analytics", "bitly alternative", "short links"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className} suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
'use client';

import URLShortener from '@/components/URLShortener';
import { GlassCard } from '@/components/ui/GlassCard';
import { Zap, BarChart3, Globe, Shield, Sparkles, TrendingUp } from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-dark-bg relative overflow-hidden">
      {/* Animated mesh background */}
      <div className="fixed inset-0 bg-mesh opacity-60 animate-pulse" style={{ animationDuration: '8s' }} />

      {/* Floating orbs */}
      <div className="fixed top-20 left-10 w-72 h-72 bg-neon-cyan rounded-full opacity-20 blur-3xl animate-float" />
      <div className="fixed bottom-20 right-10 w-96 h-96 bg-neon-purple rounded-full opacity-20 blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      <div className="fixed top-1/2 left-1/2 w-80 h-80 bg-neon-pink rounded-full opacity-15 blur-3xl animate-float" style={{ animationDelay: '4s' }} />

      <div className="relative z-10">
        {/* Navigation */}
        <nav className="glass-strong border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-20">
              <div className="flex items-center gap-3 group cursor-pointer">
                <div className="w-10 h-10 gradient-holographic rounded-xl flex items-center justify-center transform group-hover:rotate-180 transition-transform duration-500">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-bold text-gradient-holographic">
                  Super Intelligence URLs
                </span>
                <span className="px-2 py-1 text-xs font-semibold bg-neon-cyan/20 text-neon-cyan rounded-full border border-neon-cyan/30 animate-pulse">
                  2030
                </span>
              </div>
              <div className="flex items-center gap-6">
                <Link
                  href="/dashboard/links"
                  className="text-sm font-medium text-gray-300 hover:text-neon-cyan transition-colors"
                >
                  My Links
                </Link>
                <Link
                  href="/dashboard/analytics"
                  className="px-4 py-2 rounded-lg glass hover:glass-strong text-sm font-medium text-white transition-all hover:scale-105"
                >
                  Analytics
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-20">
          <div className="text-center mb-16 animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 animate-scale-in">
              <div className="w-2 h-2 rounded-full bg-neon-cyan animate-pulse" />
              <span className="text-sm text-gray-300">Powered by AI • Real-time Analytics</span>
            </div>

            <h1 className="text-6xl md:text-8xl font-extrabold mb-6 leading-tight">
              <span className="text-white">Shorten URLs with</span>
              <br />
              <span className="text-gradient-holographic animate-gradient">
                Superintelligence
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto leading-relaxed">
              Create short links, track every click with{' '}
              <span className="text-neon-cyan font-semibold">advanced AI analytics</span>,
              and understand your audience like never before.
            </p>

            <div className="flex items-center justify-center gap-4 mt-8">
              <div className="flex items-center gap-2 text-gray-400">
                <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                <span className="text-sm">2.4M+ URLs shortened</span>
              </div>
              <div className="w-1 h-1 rounded-full bg-gray-600" />
              <div className="flex items-center gap-2 text-gray-400">
                <TrendingUp className="w-4 h-4 text-neon-cyan" />
                <span className="text-sm">99.9% uptime</span>
              </div>
            </div>
          </div>

          {/* URL Shortener */}
          <div className="mb-24">
            <URLShortener />
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-24">
            <GlassCard glow="cyan" className="text-center group">
              <div className="w-16 h-16 gradient-holographic rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Lightning Fast</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Redirects in &lt;50ms with quantum-optimized Base62 algorithm
              </p>
              <div className="mt-4 pt-4 border-t border-white/10">
                <span className="text-2xl font-bold text-neon-cyan">0.007ms</span>
                <p className="text-xs text-gray-500 mt-1">Average generation time</p>
              </div>
            </GlassCard>

            <GlassCard glow="purple" className="text-center group">
              <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">AI Analytics</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Machine learning powered insights on device, location, and behavior
              </p>
              <div className="mt-4 pt-4 border-t border-white/10">
                <span className="text-2xl font-bold text-green-400">15+</span>
                <p className="text-xs text-gray-500 mt-1">Data points per click</p>
              </div>
            </GlassCard>

            <GlassCard glow="pink" className="text-center group">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                <Globe className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Global Tracking</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                IP geolocation with 99.5% accuracy across 195+ countries
              </p>
              <div className="mt-4 pt-4 border-t border-white/10">
                <span className="text-2xl font-bold text-pink-400">195+</span>
                <p className="text-xs text-gray-500 mt-1">Countries tracked</p>
              </div>
            </GlassCard>

            <GlassCard glow="cyan" className="text-center group">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">100% Free</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Unlimited links, unlimited analytics. Forever. No credit card.
              </p>
              <div className="mt-4 pt-4 border-t border-white/10">
                <span className="text-2xl font-bold text-orange-400">∞</span>
                <p className="text-xs text-gray-500 mt-1">Unlimited everything</p>
              </div>
            </GlassCard>
          </div>

          {/* Stats Section */}
          <GlassCard intensity="strong" className="relative overflow-hidden">
            <div className="absolute inset-0 gradient-holographic opacity-5" />
            <div className="relative grid md:grid-cols-3 gap-8 text-center">
              <div className="group cursor-pointer">
                <div className="text-6xl font-black text-gradient-holographic mb-3 group-hover:scale-110 transition-transform">
                  &lt;50ms
                </div>
                <div className="text-gray-400 font-medium">Average Redirect Time</div>
                <div className="text-sm text-gray-500 mt-2">Industry leading performance</div>
              </div>
              <div className="group cursor-pointer">
                <div className="text-6xl font-black text-gradient-neon mb-3 group-hover:scale-110 transition-transform">
                  99.9%
                </div>
                <div className="text-gray-400 font-medium">Uptime Guarantee</div>
                <div className="text-sm text-gray-500 mt-2">Enterprise-grade reliability</div>
              </div>
              <div className="group cursor-pointer">
                <div className="text-6xl font-black text-white mb-3 group-hover:scale-110 transition-transform">
                  <span className="text-gradient-holographic">∞</span>
                </div>
                <div className="text-gray-400 font-medium">Unlimited Links</div>
                <div className="text-sm text-gray-500 mt-2">No limits, ever</div>
              </div>
            </div>
          </GlassCard>

          {/* CTA Section */}
          <div className="text-center mt-24">
            <GlassCard intensity="strong" className="inline-block">
              <div className="flex flex-col md:flex-row items-center gap-6">
                <div className="text-left">
                  <h3 className="text-2xl font-bold text-white mb-2">
                    Ready to experience the future?
                  </h3>
                  <p className="text-gray-400">Start shortening URLs with AI-powered analytics</p>
                </div>
                <button className="px-8 py-4 gradient-holographic text-white font-semibold rounded-xl hover:scale-105 transition-transform glow-cyan whitespace-nowrap">
                  Get Started Free
                </button>
              </div>
            </GlassCard>
          </div>
        </div>

        {/* Footer */}
        <footer className="glass-strong border-t border-white/10 mt-32">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 text-gray-400 mb-4">
                <span>Built with</span>
                <span className="text-neon-pink">♥</span>
                <span>using Next.js, FastAPI, and Supabase</span>
              </div>
              <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
                <span>© 2025 SuperintelligenceURLs</span>
                <span>•</span>
                <span>Powered by Superintelligence</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
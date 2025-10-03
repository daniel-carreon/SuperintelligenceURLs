'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { getAnalytics, AnalyticsResponse } from '@/lib/api';
import { GlassCard } from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, Globe, Monitor, ExternalLink, RefreshCw, Sparkles, Activity, Youtube, Clock } from 'lucide-react';
import Link from 'next/link';

// Holographic color palette for charts
const COLORS = ['#00fff5', '#0066ff', '#8b5cf6', '#ff006e', '#ff6b35', '#10b981'];

function AnalyticsContent() {
  const searchParams = useSearchParams();
  const [shortCode, setShortCode] = useState(searchParams?.get('code') || '');
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchAnalytics = async (code: string) => {
    if (!code) {
      setError('Please enter a short code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await getAnalytics(code);
      setAnalytics(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics');
      setAnalytics(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const code = searchParams?.get('code');
    if (code) {
      setShortCode(code);
      fetchAnalytics(code);
    }
  }, [searchParams]);

  // Prepare chart data
  const deviceData = analytics
    ? Object.entries(analytics.device_breakdown).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value,
      }))
    : [];

  const referrerData = analytics?.recent_clicks && Array.isArray(analytics.recent_clicks)
    ? Object.entries(
        analytics.recent_clicks.reduce((acc, click) => {
          const source = click.referrer_source || 'Unknown';
          acc[source] = (acc[source] || 0) + 1;
          return acc;
        }, {} as Record<string, number>)
      ).map(([name, value]) => ({ name, clicks: value }))
    : [];

  const countryData = analytics?.recent_clicks && Array.isArray(analytics.recent_clicks)
    ? Object.entries(
        analytics.recent_clicks.reduce((acc, click) => {
          const country = click.country_name || 'Unknown';
          acc[country] = (acc[country] || 0) + 1;
          return acc;
        }, {} as Record<string, number>)
      )
        .map(([name, clicks]) => ({ name, clicks }))
        .sort((a, b) => b.clicks - a.clicks)
        .slice(0, 5)
    : [];

  // Prepare video sources data
  const videoSourcesData = analytics?.video_sources
    ? Object.entries(analytics.video_sources).map(([videoKey, count]) => {
        const [platform, videoId] = videoKey.split(':');
        return { platform, videoId, clicks: count };
      }).sort((a, b) => b.clicks - a.clicks)
    : [];

  return (
    <div className="min-h-screen bg-dark-bg relative overflow-hidden">
      {/* Animated mesh background */}
      <div className="fixed inset-0 bg-mesh opacity-60 animate-pulse" style={{ animationDuration: '8s' }} />

      {/* Floating orbs */}
      <div className="fixed top-20 left-10 w-72 h-72 bg-neon-cyan rounded-full opacity-20 blur-3xl animate-float" />
      <div className="fixed bottom-20 right-10 w-96 h-96 bg-neon-purple rounded-full opacity-20 blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      <div className="fixed top-1/2 left-1/2 w-80 h-80 bg-neon-pink rounded-full opacity-15 blur-3xl animate-float" style={{ animationDelay: '4s' }} />

      <div className="relative z-10">
        {/* Header */}
        <nav className="glass-strong border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-20">
              <Link href="/" className="flex items-center gap-3 group">
                <div className="w-10 h-10 gradient-holographic rounded-xl flex items-center justify-center transform group-hover:rotate-180 transition-transform duration-500">
                  <Activity className="w-6 h-6 text-white" />
                </div>
                <div>
                  <span className="text-2xl font-bold text-gradient-holographic block">
                    LinkProxy Analytics
                  </span>
                  <span className="text-xs text-gray-400">Real-time Intelligence</span>
                </div>
              </Link>
              <Link href="/">
                <Button variant="secondary">← Back to Home</Button>
              </Link>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Search Bar */}
          <div className="mb-12 animate-fade-in">
            <div className="glass-strong rounded-2xl p-6 border border-neon-cyan/30 glow-cyan">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  fetchAnalytics(shortCode);
                }}
                className="flex gap-4"
              >
                <Input
                  placeholder="Enter short code (e.g., QnaF5M)"
                  value={shortCode}
                  onChange={(e) => setShortCode(e.target.value)}
                  className="flex-1"
                  error={error}
                />
                <Button type="submit" variant="primary" size="lg" isLoading={loading} className="flex items-center gap-2 px-8">
                  <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                  Load Analytics
                </Button>
              </form>
            </div>
          </div>

          {analytics && (
            <div className="space-y-8 animate-fade-in">
              {/* Header Info */}
              <div className="glass-strong rounded-2xl p-8 border border-neon-cyan/30 glow-cyan relative overflow-hidden">
                <div className="absolute inset-0 gradient-holographic opacity-5" />
                <div className="relative z-10 flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-3 h-3 rounded-full bg-neon-cyan animate-pulse" />
                      <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Link Intelligence</span>
                    </div>
                    <h2 className="text-4xl font-black text-gradient-holographic mb-4">
                      /{analytics.short_code}
                    </h2>
                    <a
                      href={analytics.original_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-neon-cyan hover:text-neon-blue flex items-center gap-2 transition-colors group"
                    >
                      <span className="break-all">{analytics.original_url}</span>
                      <ExternalLink className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </a>
                  </div>
                  <div className="glass rounded-xl p-4 border border-white/10 text-right">
                    <p className="text-xs font-semibold text-gray-400 mb-1 uppercase">Created</p>
                    <p className="text-lg font-bold text-white">
                      {new Date(analytics.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid md:grid-cols-2 gap-6">
                <GlassCard glow="cyan" className="relative overflow-hidden">
                  <div className="absolute inset-0 gradient-holographic opacity-5" />
                  <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-12 h-12 gradient-holographic rounded-xl flex items-center justify-center">
                        <TrendingUp className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Total Clicks</h3>
                        <p className="text-xs text-gray-500">Real-time tracking</p>
                      </div>
                    </div>
                    <div className="text-6xl font-black text-gradient-holographic mb-3">
                      {analytics.total_clicks.toLocaleString()}
                    </div>
                    <div className="flex items-center gap-2 text-neon-cyan">
                      <div className="w-2 h-2 rounded-full bg-neon-cyan animate-pulse" />
                      <p className="text-sm font-medium">
                        {analytics.unique_visitors.toLocaleString()} unique visitors
                      </p>
                    </div>
                  </div>
                </GlassCard>

                <GlassCard glow="purple" className="relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5" />
                  <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                        <Monitor className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="text-base font-bold text-white">Device Breakdown</h3>
                    </div>
                    <ResponsiveContainer width="100%" height={220}>
                      <PieChart>
                        <Pie
                          data={deviceData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={85}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {deviceData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'rgba(26, 26, 36, 0.95)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '12px',
                            color: '#fff'
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </GlassCard>
              </div>

              {/* Charts Row */}
              <div className="grid md:grid-cols-2 gap-6">
                <GlassCard glow="pink" className="relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-cyan-500/5" />
                  <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-600 rounded-xl flex items-center justify-center">
                        <Globe className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-white">Top Countries</h3>
                        <p className="text-xs text-gray-400">Geographic distribution</p>
                      </div>
                    </div>
                    <ResponsiveContainer width="100%" height={280}>
                      <BarChart data={countryData}>
                        <XAxis
                          dataKey="name"
                          stroke="#9ca3af"
                          style={{ fontSize: '12px' }}
                        />
                        <YAxis
                          stroke="#9ca3af"
                          style={{ fontSize: '12px' }}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'rgba(26, 26, 36, 0.95)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '12px',
                            color: '#fff'
                          }}
                        />
                        <Bar
                          dataKey="clicks"
                          fill="url(#countryGradient)"
                          radius={[8, 8, 0, 0]}
                        />
                        <defs>
                          <linearGradient id="countryGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#10b981" stopOpacity={1} />
                            <stop offset="100%" stopColor="#059669" stopOpacity={0.8} />
                          </linearGradient>
                        </defs>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </GlassCard>

                <GlassCard glow="cyan" className="relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-red-500/5" />
                  <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center">
                        <ExternalLink className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-white">Traffic Sources</h3>
                        <p className="text-xs text-gray-400">Referrer breakdown</p>
                      </div>
                    </div>
                    <ResponsiveContainer width="100%" height={280}>
                      <BarChart data={referrerData} layout="vertical">
                        <XAxis
                          type="number"
                          stroke="#9ca3af"
                          style={{ fontSize: '12px' }}
                        />
                        <YAxis
                          dataKey="name"
                          type="category"
                          width={100}
                          stroke="#9ca3af"
                          style={{ fontSize: '12px' }}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'rgba(26, 26, 36, 0.95)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '12px',
                            color: '#fff'
                          }}
                        />
                        <Bar
                          dataKey="clicks"
                          fill="url(#referrerGradient)"
                          radius={[0, 8, 8, 0]}
                        />
                        <defs>
                          <linearGradient id="referrerGradient" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="0%" stopColor="#f59e0b" stopOpacity={1} />
                            <stop offset="100%" stopColor="#ef4444" stopOpacity={0.8} />
                          </linearGradient>
                        </defs>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </GlassCard>
              </div>

              {/* Video Sources Widget */}
              {videoSourcesData && videoSourcesData.length > 0 && (
                <GlassCard glow="pink" className="relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-pink-500/5 to-purple-500/5" />
                  <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-purple-600 rounded-xl flex items-center justify-center">
                        <Youtube className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-white">Video Traffic Sources</h3>
                        <p className="text-xs text-gray-400">Links clicked from videos</p>
                      </div>
                    </div>
                    <div className="space-y-3">
                      {videoSourcesData.slice(0, 5).map((video, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 glass rounded-xl border border-white/10 hover:border-neon-cyan/50 transition-colors group">
                          <div className="flex items-center gap-4 flex-1">
                            <div className="flex-shrink-0">
                              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-500 to-pink-600 flex items-center justify-center">
                                <Youtube className="w-5 h-5 text-white" />
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-xs font-semibold text-neon-cyan uppercase">{video.platform}</span>
                                <span className="w-1 h-1 rounded-full bg-gray-600" />
                                <span className="text-xs text-gray-400 font-mono truncate">{video.videoId}</span>
                              </div>
                              <a
                                href={`https://${video.platform}.com/watch?v=${video.videoId}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-gray-300 hover:text-neon-cyan transition-colors flex items-center gap-1 group-hover:underline"
                              >
                                View on {video.platform.charAt(0).toUpperCase() + video.platform.slice(1)}
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            </div>
                          </div>
                          <div className="flex-shrink-0 ml-4">
                            <div className="text-right">
                              <div className="text-2xl font-black text-gradient-holographic">{video.clicks}</div>
                              <div className="text-xs text-gray-400">clicks</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </GlassCard>
              )}

              {/* Recent Clicks Table */}
              <GlassCard intensity="strong" className="relative overflow-hidden">
                <div className="absolute inset-0 gradient-holographic opacity-5" />
                <div className="relative z-10">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-3 h-3 rounded-full bg-neon-cyan animate-pulse" />
                    <h3 className="text-xl font-bold text-white">Recent Clicks</h3>
                    <span className="text-xs text-gray-400">Live activity feed</span>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-white/10">
                          <th className="px-4 py-4 text-left font-semibold text-gray-400 uppercase tracking-wider text-xs">Time</th>
                          <th className="px-4 py-4 text-left font-semibold text-gray-400 uppercase tracking-wider text-xs">Location</th>
                          <th className="px-4 py-4 text-left font-semibold text-gray-400 uppercase tracking-wider text-xs">Device</th>
                          <th className="px-4 py-4 text-left font-semibold text-gray-400 uppercase tracking-wider text-xs">Source</th>
                          <th className="px-4 py-4 text-left font-semibold text-gray-400 uppercase tracking-wider text-xs">Video</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        {analytics?.recent_clicks && Array.isArray(analytics.recent_clicks) && analytics.recent_clicks.length > 0 ? (
                          analytics.recent_clicks.map((click, idx) => (
                          <tr key={click.id} className="hover:bg-white/5 transition-colors group">
                            <td className="px-4 py-4 text-gray-300 font-mono text-xs">
                              {new Date(click.clicked_at).toLocaleString()}
                            </td>
                            <td className="px-4 py-4">
                              <div className="flex items-center gap-2">
                                <Globe className="w-4 h-4 text-neon-cyan" />
                                <span className="text-white font-medium">{click.country_name}</span>
                                {click.city && <span className="text-gray-500 text-xs">• {click.city}</span>}
                              </div>
                            </td>
                            <td className="px-4 py-4">
                              <span className="px-3 py-1 glass rounded-lg text-xs font-semibold text-white border border-white/10">
                                {click.device_type}
                              </span>
                            </td>
                            <td className="px-4 py-4">
                              <span className="px-3 py-1 bg-neon-cyan/10 text-neon-cyan rounded-lg text-xs font-semibold border border-neon-cyan/30">
                                {click.referrer_source}
                              </span>
                            </td>
                            <td className="px-4 py-4">
                              {click.video_platform ? (
                                <div className="flex items-center gap-2">
                                  <Youtube className="w-4 h-4 text-red-500" />
                                  <span className="text-xs font-semibold text-red-400 uppercase">{click.video_platform}</span>
                                  <span className="text-gray-500 text-xs font-mono">({click.video_id?.substring(0, 8)}...)</span>
                                </div>
                              ) : (
                                <span className="text-gray-600 text-xs">-</span>
                              )}
                            </td>
                          </tr>
                        ))
                        ) : (
                          <tr>
                            <td colSpan={5} className="px-4 py-12 text-center">
                              <div className="text-gray-400">
                                <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                <p className="text-sm">No clicks yet. Share your link to start tracking!</p>
                              </div>
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </GlassCard>
            </div>
          )}

          {!analytics && !loading && !error && (
            <GlassCard intensity="strong" className="text-center py-20 relative overflow-hidden">
              <div className="absolute inset-0 gradient-holographic opacity-5" />
              <div className="relative z-10">
                <div className="w-24 h-24 gradient-holographic rounded-3xl flex items-center justify-center mx-auto mb-8 animate-float">
                  <Activity className="w-12 h-12 text-white" />
                </div>
                <h3 className="text-3xl font-black text-gradient-holographic mb-4">
                  Enter a short code to view analytics
                </h3>
                <p className="text-gray-400 text-lg max-w-md mx-auto">
                  Get detailed real-time insights into your link performance powered by AI
                </p>
              </div>
            </GlassCard>
          )}
        </div>
      </div>
    </div>
  );
}

export default function AnalyticsPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen"><div className="text-white">Loading analytics...</div></div>}>
      <AnalyticsContent />
    </Suspense>
  );
}
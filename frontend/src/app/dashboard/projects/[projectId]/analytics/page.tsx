'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getProjectAnalytics, getProjectLinks, type VideoProjectAnalytics, type ProjectLink } from '@/lib/video-projects-api';
import { getAnalytics, type AnalyticsResponse } from '@/lib/api';
import { GlassCard } from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import { AddLinksToProjectModal } from '@/components/AddLinksToProjectModal';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, Globe, Monitor, ArrowLeft, Youtube, Users, MapPin, Plus, Link2 } from 'lucide-react';
import Link from 'next/link';

// Holographic color palette
const COLORS = ['#00fff5', '#0066ff', '#8b5cf6', '#ff006e', '#ff6b35', '#10b981'];

export default function ProjectAnalyticsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params?.projectId as string;

  const [projectAnalytics, setProjectAnalytics] = useState<VideoProjectAnalytics | null>(null);
  const [projectLinks, setProjectLinks] = useState<ProjectLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddLinksModal, setShowAddLinksModal] = useState(false);

  useEffect(() => {
    if (projectId) {
      loadAnalytics();
    }
  }, [projectId]);

  const loadAnalytics = async () => {
    setLoading(true);
    setError('');

    try {
      const [analytics, links] = await Promise.all([
        getProjectAnalytics(projectId),
        getProjectLinks(projectId),
      ]);

      setProjectAnalytics(analytics);
      setProjectLinks(links);
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error || !projectAnalytics) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
        <GlassCard intensity="strong" className="max-w-md w-full text-center">
          <h3 className="text-xl font-bold text-red-400 mb-2">Error</h3>
          <p className="text-gray-400 mb-4">{error || 'Project not found'}</p>
          <Link href="/dashboard/projects">
            <Button variant="secondary">← Back to Projects</Button>
          </Link>
        </GlassCard>
      </div>
    );
  }

  // Prepare data for links comparison chart
  const linksComparisonData = projectLinks
    .map((link) => ({
      name: `/${link.short_code}`,
      clicks: link.click_count,
      title: link.title || link.short_code,
    }))
    .sort((a, b) => b.clicks - a.clicks);

  // Device breakdown (mock data - to be replaced with actual aggregated data)
  const deviceData = [
    { name: 'Desktop', value: projectAnalytics.desktop_clicks || 0 },
    { name: 'Mobile', value: projectAnalytics.mobile_clicks || 0 },
    { name: 'Tablet', value: projectAnalytics.tablet_clicks || 0 },
  ].filter((d) => d.value > 0);

  return (
    <div className="min-h-screen bg-dark-bg relative overflow-hidden">
      {/* Animated mesh background */}
      <div className="fixed inset-0 bg-gradient-mesh opacity-60 animate-pulse" style={{ animationDuration: '8s' }} />

      {/* Floating orbs */}
      <div className="fixed top-20 left-10 w-72 h-72 bg-neon-cyan rounded-full opacity-20 blur-3xl animate-float" />
      <div className="fixed bottom-20 right-10 w-96 h-96 bg-neon-purple rounded-full opacity-20 blur-3xl animate-float" style={{ animationDelay: '2s' }} />

      <div className="relative z-10">
        {/* Header */}
        <nav className="glass-strong border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-20">
              <Link href="/dashboard/projects" className="flex items-center gap-3 group">
                <div className="w-10 h-10 gradient-holographic rounded-xl flex items-center justify-center">
                  <ArrowLeft className="w-6 h-6 text-white" />
                </div>
                <div>
                  <span className="text-2xl font-bold text-gradient-holographic block">
                    Project Analytics
                  </span>
                  <span className="text-xs text-gray-400">Aggregated Metrics</span>
                </div>
              </Link>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8">
          {/* Project Header */}
          <GlassCard glow="cyan" className="relative overflow-hidden">
            <div className="absolute inset-0 gradient-holographic opacity-5" />
            <div className="relative z-10 flex gap-6">
              {/* Thumbnail */}
              {projectAnalytics.youtube_video_id && (
                <div className="w-40 h-28 rounded-xl overflow-hidden flex-shrink-0 relative group">
                  <img
                    src={projectAnalytics.thumbnail_url || `https://img.youtube.com/vi/${projectAnalytics.youtube_video_id}/hqdefault.jpg`}
                    alt={projectAnalytics.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                  />
                  <div className="absolute top-2 right-2 w-6 h-6 bg-red-600 rounded flex items-center justify-center">
                    <Youtube className="w-4 h-4 text-white" />
                  </div>
                </div>
              )}

              {/* Info */}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 rounded-full bg-neon-cyan animate-pulse" />
                  <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Video Project
                  </span>
                </div>
                <h1 className="text-3xl font-black text-gradient-holographic mb-3">
                  {projectAnalytics.title}
                </h1>
                {projectAnalytics.youtube_url && (
                  <a
                    href={projectAnalytics.youtube_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-neon-cyan hover:text-neon-blue transition-colors inline-flex items-center gap-2"
                  >
                    Watch on YouTube →
                  </a>
                )}
              </div>
            </div>
          </GlassCard>

          {/* Stats Grid */}
          <div className="grid md:grid-cols-4 gap-6">
            <GlassCard glow="cyan">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 gradient-holographic rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-xs font-semibold text-gray-400 uppercase">Total Clicks</h3>
                </div>
              </div>
              <div className="text-4xl font-black text-gradient-holographic">
                {projectAnalytics.total_clicks || 0}
              </div>
            </GlassCard>

            <GlassCard glow="purple">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-neon-purple/20 rounded-xl flex items-center justify-center">
                  <Users className="w-5 h-5 text-neon-purple" />
                </div>
                <div>
                  <h3 className="text-xs font-semibold text-gray-400 uppercase">Unique Visitors</h3>
                </div>
              </div>
              <div className="text-4xl font-black text-neon-purple">
                {projectAnalytics.unique_visitors || 0}
              </div>
            </GlassCard>

            <GlassCard glow="pink">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-neon-pink/20 rounded-xl flex items-center justify-center">
                  <Globe className="w-5 h-5 text-neon-pink" />
                </div>
                <div>
                  <h3 className="text-xs font-semibold text-gray-400 uppercase">Countries</h3>
                </div>
              </div>
              <div className="text-4xl font-black text-neon-pink">
                {projectAnalytics.countries_reached || 0}
              </div>
            </GlassCard>

            <GlassCard>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 glass rounded-xl flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-neon-cyan" />
                </div>
                <div>
                  <h3 className="text-xs font-semibold text-gray-400 uppercase">Links</h3>
                </div>
              </div>
              <div className="text-4xl font-black text-white">
                {projectAnalytics.total_links || projectLinks.length}
              </div>
            </GlassCard>
          </div>

          {/* Charts Row */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Links Comparison Bar Chart */}
            <GlassCard glow="cyan">
              <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                <BarChart className="w-5 h-5 text-neon-cyan" />
                Links Performance
              </h3>
              {linksComparisonData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={linksComparisonData}>
                    <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
                    <YAxis stroke="#9ca3af" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(26, 26, 36, 0.95)',
                        border: '1px solid rgba(0, 255, 245, 0.3)',
                        borderRadius: '12px',
                        backdropFilter: 'blur(10px)',
                      }}
                    />
                    <Bar dataKey="clicks" fill="url(#holographicGradient)" radius={[8, 8, 0, 0]} />
                    <defs>
                      <linearGradient id="holographicGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#00fff5" stopOpacity={0.9} />
                        <stop offset="100%" stopColor="#0066ff" stopOpacity={0.6} />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[300px] flex items-center justify-center text-gray-500">
                  No links data available
                </div>
              )}
            </GlassCard>

            {/* Device Breakdown Pie Chart */}
            <GlassCard glow="purple">
              <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                <Monitor className="w-5 h-5 text-neon-purple" />
                Device Breakdown
              </h3>
              {deviceData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={deviceData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                      label
                    >
                      {deviceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[300px] flex items-center justify-center text-gray-500">
                  No device data available
                </div>
              )}
            </GlassCard>
          </div>

          {/* Links Table */}
          <GlassCard glow="cyan">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-white">
                All Links in Project
              </h3>
              {projectLinks.length > 0 && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => setShowAddLinksModal(true)}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Links
                </Button>
              )}
            </div>

            {projectLinks.length === 0 ? (
              <div className="text-center py-16 relative overflow-hidden">
                <div className="absolute inset-0 gradient-holographic opacity-5" />
                <div className="relative z-10">
                  <div className="w-20 h-20 gradient-holographic rounded-2xl flex items-center justify-center mx-auto mb-6 animate-float">
                    <Link2 className="w-10 h-10 text-white" />
                  </div>
                  <h4 className="text-xl font-bold text-white mb-3">
                    No links yet
                  </h4>
                  <p className="text-gray-400 mb-8 max-w-md mx-auto">
                    Add your first link to this project to start tracking analytics
                  </p>
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={() => setShowAddLinksModal(true)}
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    Add Your First Link
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {projectLinks.map((link) => (
                  <div
                    key={link.id}
                    className="glass hover:glass-strong rounded-lg p-4 transition-all cursor-pointer"
                    onClick={() => router.push(`/dashboard/analytics?code=${link.short_code}`)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <span className="text-lg font-black text-gradient-holographic">
                            /{link.short_code}
                          </span>
                          {link.title && (
                            <span className="glass px-2 py-0.5 rounded text-xs font-semibold text-white">
                              {link.title}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-400 truncate">{link.original_url}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-neon-cyan">{link.click_count}</div>
                        <div className="text-xs text-gray-500">clicks</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </GlassCard>
        </div>
      </div>

      {/* Add Links Modal */}
      {showAddLinksModal && (
        <AddLinksToProjectModal
          projectId={projectId}
          projectTitle={projectAnalytics?.title || 'Video Project'}
          onClose={() => setShowAddLinksModal(false)}
          onSuccess={() => {
            setShowAddLinksModal(false);
            loadAnalytics(); // Reload analytics and links
          }}
        />
      )}
    </div>
  );
}

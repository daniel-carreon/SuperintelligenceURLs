'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getAllURLs, deleteURL } from '@/lib/api';
import { GlassCard } from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import { Link2, TrendingUp, Copy, Check, ExternalLink, LogOut, Video, BarChart3, Trash2, FolderPlus } from 'lucide-react';
import { AssignLinkToProjectModal } from '@/components/AssignLinkToProjectModal';

export default function AllLinksPage() {
  const router = useRouter();
  const [links, setLinks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [assignModalLink, setAssignModalLink] = useState<{id: string; title: string; shortCode: string} | null>(null);

  useEffect(() => {
    loadLinks();
  }, []);

  const loadLinks = async () => {
    try {
      console.log('🚀 [DEBUG] Loading all links...');
      setLoading(true);
      const data = await getAllURLs();
      console.log('✅ [DEBUG] Loaded', data.length, 'links');
      setLinks(data);
    } catch (error) {
      console.error('❌ [DEBUG] Failed to load links:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (shortCode: string, id: string) => {
    const url = `${window.location.origin}/${shortCode}`;
    navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleLogout = async () => {
    router.push('/login');
  };

  const handleDelete = async (shortCode: string) => {
    if (!confirm('⚠️ Delete this link permanently?\n\nThis will remove all associated analytics data. This action cannot be undone.')) {
      return;
    }

    try {
      console.log('🗑️ [DEBUG] Deleting link:', shortCode);
      await deleteURL(shortCode);
      console.log('✅ [DEBUG] Link deleted successfully');
      await loadLinks();
    } catch (error: any) {
      console.error('❌ [DEBUG] Failed to delete link:', error);
      alert(error.message || 'Failed to delete link');
    }
  };

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
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 gradient-holographic rounded-xl flex items-center justify-center">
                    <Link2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <span className="text-2xl font-bold text-gradient-holographic block">All Links</span>
                    <span className="text-xs text-gray-400">Complete link repository</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Button variant="secondary" onClick={() => router.push('/dashboard/projects')}>
                  <Video className="w-4 h-4 mr-2" />
                  Video Projects
                </Button>
                <Button variant="secondary" onClick={() => router.push('/')}>
                  ← Home
                </Button>
                <Button variant="ghost" size="sm" onClick={handleLogout}>
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Section */}
          <div className="mb-12 animate-fade-in">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-neon-cyan animate-pulse" />
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                All Links Dashboard
              </span>
            </div>
            <h1 className="text-5xl font-black text-gradient-holographic mb-4">
              Your Complete Link Library
            </h1>
            <p className="text-gray-400 text-lg max-w-3xl">
              View all your shortened URLs in one place. Track clicks and manage your link portfolio.
            </p>
          </div>

          {/* Stats Row */}
          {!loading && links.length > 0 && (
            <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
              <GlassCard glow="cyan" className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 gradient-holographic rounded-xl flex items-center justify-center">
                    <Link2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-black text-neon-cyan">{links.length}</div>
                    <div className="text-sm text-gray-400">Total Links</div>
                  </div>
                </div>
              </GlassCard>

              <GlassCard glow="purple" className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 gradient-holographic rounded-xl flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-black text-neon-purple">
                      {links.reduce((sum, link) => sum + (link.click_count || 0), 0)}
                    </div>
                    <div className="text-sm text-gray-400">Total Clicks</div>
                  </div>
                </div>
              </GlassCard>

              <GlassCard glow="pink" className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 gradient-holographic rounded-xl flex items-center justify-center">
                    <ExternalLink className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-black text-neon-pink">
                      {links.filter(l => (l.click_count || 0) > 0).length}
                    </div>
                    <div className="text-sm text-gray-400">Active Links</div>
                  </div>
                </div>
              </GlassCard>
            </div>
          )}

          {/* Links Grid */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <div className="w-16 h-16 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-gray-400">Loading your links...</p>
              </div>
            </div>
          ) : links.length === 0 ? (
            <GlassCard intensity="strong" className="text-center py-20">
              <div className="w-24 h-24 gradient-holographic rounded-3xl flex items-center justify-center mx-auto mb-8">
                <Link2 className="w-12 h-12 text-white" />
              </div>
              <h3 className="text-3xl font-black text-gradient-holographic mb-4">No links yet</h3>
              <p className="text-gray-400 text-lg mb-8">
                Create your first shortened URL from the home page
              </p>
              <Button variant="primary" size="lg" onClick={() => router.push('/')}>
                Create Link
              </Button>
            </GlassCard>
          ) : (
            <div className="space-y-3">
              {links.map((link, idx) => (
                <GlassCard
                  key={link.id}
                  glow="cyan"
                  className="p-6 hover:scale-[1.01] transition-all duration-200 animate-fade-in"
                  style={{ animationDelay: `${idx * 30}ms` }}
                >
                  <div className="flex items-center justify-between gap-6">
                    {/* Link Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-8 h-8 gradient-holographic rounded-lg flex items-center justify-center flex-shrink-0">
                          <Link2 className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-mono text-lg font-bold text-neon-cyan">
                            /{link.short_code}
                          </div>
                          {link.title && (
                            <div className="text-sm text-gray-300 truncate">{link.title}</div>
                          )}
                        </div>
                      </div>
                      <div className="ml-11 text-sm text-gray-400 truncate">
                        → {link.original_url}
                      </div>
                    </div>

                    {/* Stats & Actions */}
                    <div className="flex items-center gap-6">
                      <div className="text-center">
                        <div className="text-2xl font-black text-neon-purple">
                          {link.click_count || 0}
                        </div>
                        <div className="text-xs text-gray-500">clicks</div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setAssignModalLink({ id: link.id, title: link.title, shortCode: link.short_code })}
                          className="w-10 h-10 glass hover:glass-strong rounded-lg flex items-center justify-center transition-all group"
                          title="Assign to project"
                        >
                          <FolderPlus className="w-5 h-5 text-gray-400 group-hover:text-neon-purple transition-colors" />
                        </button>

                        <button
                          onClick={() => router.push(`/dashboard/analytics?code=${link.short_code}`)}
                          className="w-10 h-10 glass hover:glass-strong rounded-lg flex items-center justify-center transition-all group"
                          title="View analytics"
                        >
                          <BarChart3 className="w-5 h-5 text-gray-400 group-hover:text-neon-cyan transition-colors" />
                        </button>

                        <button
                          onClick={() => copyToClipboard(link.short_code, link.id)}
                          className="w-10 h-10 glass hover:glass-strong rounded-lg flex items-center justify-center transition-all"
                          title="Copy link"
                        >
                          {copiedId === link.id ? (
                            <Check className="w-5 h-5 text-green-400" />
                          ) : (
                            <Copy className="w-5 h-5 text-gray-400" />
                          )}
                        </button>

                        <a
                          href={link.original_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="w-10 h-10 glass hover:glass-strong rounded-lg flex items-center justify-center transition-all"
                          title="Visit original URL"
                        >
                          <ExternalLink className="w-5 h-5 text-gray-400" />
                        </a>

                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(link.short_code);
                          }}
                          className="w-10 h-10 glass hover:bg-red-500/20 rounded-lg flex items-center justify-center transition-all group"
                          title="Delete link"
                        >
                          <Trash2 className="w-5 h-5 text-gray-400 group-hover:text-red-400 transition-colors" />
                        </button>
                      </div>
                    </div>
                  </div>
                </GlassCard>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Assign to Project Modal */}
      {assignModalLink && (
        <AssignLinkToProjectModal
          urlId={assignModalLink.id}
          urlTitle={assignModalLink.title}
          shortCode={assignModalLink.shortCode}
          onClose={() => setAssignModalLink(null)}
          onSuccess={() => {
            setAssignModalLink(null);
            loadLinks();
          }}
        />
      )}
    </div>
  );
}

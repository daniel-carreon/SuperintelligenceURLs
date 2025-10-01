'use client';

import { GlassCard } from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import FoldersSidebar from '@/components/FoldersSidebar';
import { Link2, Copy, BarChart3, ExternalLink, Check, Sparkles, TrendingUp, FolderInput, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { getAllFolders, assignLinkToFolder, type Folder } from '@/lib/folders-api';
import { getAllURLs, type URLResponse } from '@/lib/api';

export default function LinksPage() {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [showFolderDropdown, setShowFolderDropdown] = useState<string | null>(null);
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [links, setLinks] = useState<URLResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFolders();
    loadLinks();
  }, []);

  const loadFolders = async () => {
    try {
      const data = await getAllFolders();
      setFolders(data);
    } catch (error) {
      console.error('Failed to load folders:', error);
    }
  };

  const loadLinks = async () => {
    try {
      setLoading(true);
      const data = await getAllURLs();
      setLinks(data.urls);
      console.log(`✅ Loaded ${data.total} links from backend`);
    } catch (error) {
      console.error('Failed to load links:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (shortCode: string, id: string) => {
    const shortURL = `${window.location.origin}/${shortCode}`;
    await navigator.clipboard.writeText(shortURL);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleAssignToFolder = async (urlId: string, folderId: string) => {
    try {
      await assignLinkToFolder({ url_id: urlId, folder_id: folderId });
      setShowFolderDropdown(null);
      alert('Link assigned to folder!');
    } catch (error) {
      console.error('Failed to assign link:', error);
      alert('Failed to assign link to folder');
    }
  };

  const handleDeleteLink = async (shortCode: string) => {
    if (!confirm('¿Eliminar este link permanentemente?')) return;

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/${shortCode}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Failed to delete link');
      }

      // Remove from UI
      setLinks(links.filter(link => link.short_code !== shortCode));
      alert('Link deleted successfully!');
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Failed to delete link');
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg relative overflow-hidden flex">
      {/* Animated mesh background */}
      <div className="fixed inset-0 bg-mesh opacity-60 animate-pulse" style={{ animationDuration: '8s' }} />

      {/* Floating orbs */}
      <div className="fixed top-20 left-10 w-72 h-72 bg-neon-cyan rounded-full opacity-20 blur-3xl animate-float" />
      <div className="fixed bottom-20 right-10 w-96 h-96 bg-neon-purple rounded-full opacity-20 blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      <div className="fixed top-1/2 left-1/2 w-80 h-80 bg-neon-pink rounded-full opacity-15 blur-3xl animate-float" style={{ animationDelay: '4s' }} />

      {/* Folders Sidebar */}
      <FoldersSidebar
        selectedFolder={selectedFolder}
        onSelectFolder={setSelectedFolder}
      />

      <div className="relative z-10 flex-1 ml-80">
        {/* Header */}
        <nav className="glass-strong border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-20">
              <Link href="/" className="flex items-center gap-3 group">
                <div className="w-10 h-10 gradient-holographic rounded-xl flex items-center justify-center transform group-hover:rotate-180 transition-transform duration-500">
                  <Link2 className="w-6 h-6 text-white" />
                </div>
                <div>
                  <span className="text-2xl font-bold text-gradient-holographic block">
                    My Links
                  </span>
                  <span className="text-xs text-gray-400">Link Management</span>
                </div>
              </Link>
              <Link href="/">
                <Button variant="secondary">← Back to Home</Button>
              </Link>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="mb-12 animate-fade-in">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-neon-cyan animate-pulse" />
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Link Collection</span>
            </div>
            <h1 className="text-5xl font-black text-gradient-holographic mb-4">Your Shortened Links</h1>
            <p className="text-gray-400 text-lg">Manage and track all your short links in one superintelligent dashboard</p>
          </div>

          <div className="space-y-6">
            {loading ? (
              <GlassCard intensity="strong" className="text-center py-20">
                <div className="w-16 h-16 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-gray-400">Loading your links...</p>
              </GlassCard>
            ) : (
              (selectedFolder
                ? links.filter(link => link.folder_id === selectedFolder)
                : links
              ).map((link, idx) => (
              <GlassCard key={link.id} glow="cyan" className="relative overflow-hidden group animate-fade-in" style={{ animationDelay: `${idx * 100}ms` }}>
                <div className="absolute inset-0 gradient-holographic opacity-0 group-hover:opacity-5 transition-opacity duration-300" />
                <div className="relative z-10 flex items-start justify-between">
                  <div className="flex-1 min-w-0 space-y-4">
                    <div className="flex items-center gap-3">
                      <a
                        href={`/${link.short_code}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-3xl font-black text-gradient-holographic hover:scale-105 transition-transform flex items-center gap-3 group"
                      >
                        /{link.short_code}
                        <ExternalLink className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                      </a>
                      {link.title && (
                        <span className="px-3 py-1 glass rounded-lg text-xs font-semibold text-white border border-white/10">
                          {link.title}
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-gray-400 truncate max-w-2xl">{link.original_url}</p>

                    <div className="flex items-center gap-6 text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-10 h-10 gradient-holographic rounded-lg flex items-center justify-center">
                          <TrendingUp className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <div className="text-2xl font-bold text-neon-cyan">{link.click_count}</div>
                          <div className="text-xs text-gray-500">clicks</div>
                        </div>
                      </div>

                      <div className="h-10 w-px bg-white/10" />

                      <div className="text-gray-400">
                        <div className="text-xs text-gray-500">Created</div>
                        <div className="font-medium">{new Date(link.created_at).toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' })}</div>
                      </div>

                      {link.domain && (
                        <>
                          <div className="h-10 w-px bg-white/10" />
                          <span className="px-3 py-1 bg-neon-cyan/10 text-neon-cyan rounded-lg text-xs font-semibold border border-neon-cyan/30">
                            {link.domain}
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col gap-3 ml-6">
                    <Button
                      variant="secondary"
                      size="md"
                      onClick={() => handleCopy(link.short_code, link.id)}
                      className="min-w-[44px]"
                      title={copiedId === link.id ? "Copied!" : "Copy"}
                    >
                      {copiedId === link.id ? (
                        <Check className="w-4 h-4" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </Button>

                    {/* Assign to Folder Button */}
                    <div className="relative">
                      <Button
                        variant="secondary"
                        size="md"
                        onClick={() => setShowFolderDropdown(showFolderDropdown === link.id ? null : link.id)}
                        className="min-w-[44px]"
                        title="Assign to Folder"
                      >
                        <FolderInput className="w-4 h-4" />
                      </Button>

                      {/* Folder Dropdown */}
                      {showFolderDropdown === link.id && (
                        <div className="absolute right-0 mt-2 w-56 glass-strong rounded-xl border border-white/10 shadow-2xl z-50 max-h-64 overflow-y-auto">
                          <div className="p-2">
                            {folders.length === 0 ? (
                              <div className="text-center py-4">
                                <p className="text-xs text-gray-400">No folders yet</p>
                              </div>
                            ) : (
                              folders.map((folder) => (
                                <button
                                  key={folder.id}
                                  onClick={() => handleAssignToFolder(link.short_code, folder.id)}
                                  className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/5 text-left transition-colors"
                                >
                                  <span className="text-lg">{folder.icon}</span>
                                  <span
                                    className="w-2 h-2 rounded-full flex-shrink-0"
                                    style={{ backgroundColor: folder.color }}
                                  />
                                  <span className="text-sm text-white truncate flex-1">
                                    {folder.name}
                                  </span>
                                </button>
                              ))
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    <Link href={`/dashboard/analytics?code=${link.short_code}`}>
                      <Button variant="primary" size="md" className="min-w-[44px]" title="Analytics">
                        <BarChart3 className="w-4 h-4" />
                      </Button>
                    </Link>

                    <Button
                      variant="danger"
                      size="md"
                      onClick={() => handleDeleteLink(link.short_code)}
                      className="min-w-[44px]"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </GlassCard>
              ))
            )}
          </div>

          {!loading && links.length === 0 && (
            <GlassCard intensity="strong" className="text-center py-20 relative overflow-hidden">
              <div className="absolute inset-0 gradient-holographic opacity-5" />
              <div className="relative z-10">
                <div className="w-24 h-24 gradient-holographic rounded-3xl flex items-center justify-center mx-auto mb-8 animate-float">
                  <Link2 className="w-12 h-12 text-white" />
                </div>
                <h3 className="text-3xl font-black text-gradient-holographic mb-4">
                  No links yet
                </h3>
                <p className="text-gray-400 text-lg mb-8 max-w-md mx-auto">
                  Create your first short link to unlock the power of superintelligence
                </p>
                <Link href="/">
                  <Button variant="primary" size="lg" className="px-8">
                    <Sparkles className="w-5 h-5 mr-2" />
                    Create Short Link
                  </Button>
                </Link>
              </div>
            </GlassCard>
          )}

          <div className="mt-12 text-center">
            <Link href="/">
              <Button variant="primary" size="lg" className="px-12">
                <Sparkles className="w-5 h-5 mr-2" />
                Create New Link
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
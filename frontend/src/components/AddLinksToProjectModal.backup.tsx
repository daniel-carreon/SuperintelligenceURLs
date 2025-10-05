'use client';

import { useState, useEffect } from 'react';
import { assignLinkToProject, removeLinkFromProject, getProjectLinks, type ProjectLink } from '@/lib/video-projects-api';
import { getAllURLs, type URLResponse } from '@/lib/api';
import { GlassCard } from './ui/GlassCard';
import Button from './ui/Button';
import { Link2, Plus, Trash2, X, TrendingUp, Check } from 'lucide-react';

interface AddLinksToProjectModalProps {
  projectId: string;
  projectTitle: string;
  onClose: () => void;
  onSuccess: () => void;
}

export function AddLinksToProjectModal({
  projectId,
  projectTitle,
  onClose,
  onSuccess,
}: AddLinksToProjectModalProps) {
  const [projectLinks, setProjectLinks] = useState<ProjectLink[]>([]);
  const [availableLinks, setAvailableLinks] = useState<URLResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [addingLinkId, setAddingLinkId] = useState<string | null>(null);
  const [removingLinkId, setRemovingLinkId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadData();
  }, [projectId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [links, allUrls] = await Promise.all([
        getProjectLinks(projectId),
        getAllURLs(),
      ]);

      setProjectLinks(links);

      // Filter out links already in project
      const projectLinkIds = new Set(links.map((l) => l.id));
      const available = allUrls.filter((url) => !projectLinkIds.has(url.id));
      setAvailableLinks(available);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddLink = async (urlId: string) => {
    setAddingLinkId(urlId);
    try {
      await assignLinkToProject(urlId, projectId);
      await loadData(); // Reload to update lists
    } catch (error: any) {
      alert(error.message || 'Failed to add link');
    } finally {
      setAddingLinkId(null);
    }
  };

  const handleRemoveLink = async (urlId: string) => {
    if (!confirm('Remove this link from the project?')) return;

    setRemovingLinkId(urlId);
    try {
      await removeLinkFromProject(urlId, projectId);
      await loadData(); // Reload to update lists
    } catch (error: any) {
      alert(error.message || 'Failed to remove link');
    } finally {
      setRemovingLinkId(null);
    }
  };

  // Filter available links by search term
  const filteredAvailableLinks = availableLinks.filter(
    (link) =>
      link.short_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      link.original_url.toLowerCase().includes(searchTerm.toLowerCase()) ||
      link.title?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <GlassCard
        intensity="strong"
        glow="cyan"
        className="w-full max-w-4xl max-h-[90vh] overflow-hidden animate-scale-in relative flex flex-col"
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-10 h-10 glass hover:glass-strong rounded-lg flex items-center justify-center transition-all hover:scale-110 group z-10"
        >
          <X className="w-5 h-5 text-gray-400 group-hover:text-neon-cyan transition-colors" />
        </button>

        <div className="p-6 flex-shrink-0">
          {/* Header */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 gradient-holographic rounded-xl flex items-center justify-center">
              <Link2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gradient-holographic">
                Manage Links
              </h3>
              <p className="text-sm text-gray-400">
                {projectTitle}
              </p>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center py-12">
            <div className="w-16 h-16 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-6">
            {/* Current Links in Project */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                  <Check className="w-4 h-4 text-neon-cyan" />
                  Links in Project ({projectLinks.length})
                </h4>
              </div>

              {projectLinks.length === 0 ? (
                <div className="glass-strong rounded-xl p-8 text-center">
                  <div className="w-16 h-16 gradient-holographic rounded-2xl flex items-center justify-center mx-auto mb-4 opacity-20">
                    <Link2 className="w-8 h-8 text-white" />
                  </div>
                  <p className="text-gray-400 text-sm">
                    No links in this project yet. Add links below.
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {projectLinks.map((link) => (
                    <div
                      key={link.id}
                      className="glass hover:glass-strong rounded-xl p-4 transition-all border border-neon-cyan/20"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-lg font-black text-gradient-holographic">
                              /{link.short_code}
                            </span>
                            {link.title && (
                              <span className="glass px-2 py-0.5 rounded text-xs font-semibold text-white">
                                {link.title}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400 truncate mb-2">
                            {link.original_url}
                          </p>
                          <div className="flex items-center gap-2">
                            <div className="flex items-center gap-1.5">
                              <TrendingUp className="w-4 h-4 text-neon-cyan" />
                              <span className="text-sm font-bold text-neon-cyan">
                                {link.click_count} clicks
                              </span>
                            </div>
                          </div>
                        </div>
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => handleRemoveLink(link.id)}
                          isLoading={removingLinkId === link.id}
                          className="ml-4"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Available Links to Add */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                  <Plus className="w-4 h-4 text-neon-purple" />
                  Available Links ({availableLinks.length})
                </h4>
              </div>

              {/* Search */}
              <div className="mb-3">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search links by code, title, or URL..."
                  className="w-full h-10 px-4 glass rounded-lg text-white placeholder:text-gray-500 focus:glass-strong focus:outline-none focus:ring-2 focus:ring-neon-cyan/30"
                />
              </div>

              {availableLinks.length === 0 ? (
                <div className="glass-strong rounded-xl p-8 text-center">
                  <p className="text-gray-400 text-sm">
                    All your links are already in this project! 🎉
                  </p>
                </div>
              ) : filteredAvailableLinks.length === 0 ? (
                <div className="glass-strong rounded-xl p-8 text-center">
                  <p className="text-gray-400 text-sm">
                    No links match your search
                  </p>
                </div>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {filteredAvailableLinks.map((link) => (
                    <div
                      key={link.id}
                      className="glass hover:glass-strong rounded-xl p-4 transition-all border border-white/10"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-lg font-black text-white">
                              /{link.short_code}
                            </span>
                            {link.title && (
                              <span className="glass px-2 py-0.5 rounded text-xs font-semibold text-gray-400">
                                {link.title}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400 truncate mb-2">
                            {link.original_url}
                          </p>
                          <div className="flex items-center gap-1.5">
                            <TrendingUp className="w-4 h-4 text-gray-500" />
                            <span className="text-sm font-medium text-gray-500">
                              {link.click_count} clicks
                            </span>
                          </div>
                        </div>
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => handleAddLink(link.id)}
                          isLoading={addingLinkId === link.id}
                          className="ml-4"
                        >
                          <Plus className="w-4 h-4 mr-1" />
                          Add
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="p-6 border-t border-white/10 flex-shrink-0">
          <Button
            variant="secondary"
            className="w-full"
            onClick={() => {
              onSuccess();
              onClose();
            }}
          >
            Done
          </Button>
        </div>

        {/* Holographic glow effect */}
        <div className="absolute inset-0 gradient-holographic opacity-5 pointer-events-none" />
      </GlassCard>
    </div>
  );
}

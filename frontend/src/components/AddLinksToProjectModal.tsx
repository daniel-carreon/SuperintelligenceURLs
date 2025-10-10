'use client';

import { useState, useEffect } from 'react';
import { assignLinkToProject, getProjectLinks } from '@/lib/video-projects-api';
import { getAllURLs, createShortURL } from '@/lib/api';
import { GlassCard } from './ui/GlassCard';
import Button from './ui/Button';
import Input from './ui/Input';
import { X, Plus, Link2, List } from 'lucide-react';

interface AddLinksToProjectModalProps {
  projectId: string;
  projectTitle: string;
  onClose: () => void;
  onSuccess: () => void;
}

export function AddLinksToProjectModal({ projectId, projectTitle, onClose, onSuccess }: AddLinksToProjectModalProps) {
  const [activeTab, setActiveTab] = useState<'create' | 'assign'>('create');
  const [availableLinks, setAvailableLinks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Create new link form state
  const [originalUrl, setOriginalUrl] = useState('');
  const [title, setTitle] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (activeTab === 'assign') {
      loadLinks();
    }
  }, [activeTab]);

  const loadLinks = async () => {
    try {
      const [projectLinks, allLinks] = await Promise.all([
        getProjectLinks(projectId),
        getAllURLs(),
      ]);
      const projectLinkIds = new Set(projectLinks.map((l: any) => l.id));
      setAvailableLinks(allLinks.filter((l: any) => !projectLinkIds.has(l.id)));
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAndAssign = async () => {
    if (!originalUrl) {
      alert('Please enter a URL');
      return;
    }

    setCreating(true);
    try {
      // 1. Create the short URL
      const newLink = await createShortURL({
        original_url: originalUrl,
        title: title || undefined,
      });

      // 2. Assign it to the project
      await assignLinkToProject(newLink.id, projectId);

      // 3. Success!
      onSuccess();
      onClose();
    } catch (err: any) {
      alert(err.message || 'Failed to create link');
    } finally {
      setCreating(false);
    }
  };

  const handleAssignExisting = async (urlId: string) => {
    try {
      await assignLinkToProject(urlId, projectId);
      onSuccess();
      onClose();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <GlassCard intensity="strong" className="w-full max-w-2xl relative max-h-[80vh] overflow-auto">
        <button onClick={onClose} className="absolute top-4 right-4 w-8 h-8 glass hover:glass-strong rounded-lg flex items-center justify-center transition-all">
          <X className="w-5 h-5" />
        </button>

        <h3 className="text-2xl font-bold text-gradient-holographic mb-6">{projectTitle}</h3>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 glass p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('create')}
            className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${
              activeTab === 'create'
                ? 'gradient-holographic text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Link2 className="w-4 h-4" />
            Create New Link
          </button>
          <button
            onClick={() => setActiveTab('assign')}
            className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${
              activeTab === 'assign'
                ? 'gradient-holographic text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <List className="w-4 h-4" />
            Assign Existing
          </button>
        </div>

        {/* Create New Link Tab */}
        {activeTab === 'create' && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Original URL *
              </label>
              <Input
                type="url"
                placeholder="https://example.com/your-long-url"
                value={originalUrl}
                onChange={(e) => setOriginalUrl(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Title (optional)
              </label>
              <Input
                type="text"
                placeholder="My awesome link"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            <div className="bg-neon-cyan/10 border border-neon-cyan/30 rounded-lg p-4">
              <p className="text-sm text-gray-300">
                <strong className="text-neon-cyan">✨ Quick Create:</strong> This link will be automatically assigned to "{projectTitle}" after creation.
              </p>
            </div>

            <div className="flex gap-3 justify-end">
              <Button variant="secondary" onClick={onClose}>
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleCreateAndAssign}
                disabled={creating || !originalUrl}
              >
                {creating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4 mr-2" />
                    Create & Add to Project
                  </>
                )}
              </Button>
            </div>
          </div>
        )}

        {/* Assign Existing Links Tab */}
        {activeTab === 'assign' && (
          <>
            {loading ? (
              <div className="py-12 text-center text-gray-400">Loading available links...</div>
            ) : availableLinks.length === 0 ? (
              <div className="py-12 text-center">
                <div className="w-16 h-16 gradient-holographic rounded-2xl flex items-center justify-center mx-auto mb-4 opacity-50">
                  <List className="w-8 h-8 text-white" />
                </div>
                <p className="text-gray-400 mb-2">No links available to assign</p>
                <p className="text-sm text-gray-500">All your links are already in this project!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {availableLinks.map((link) => (
                  <div key={link.id} className="glass hover:glass-strong p-4 rounded-lg flex justify-between items-center transition-all">
                    <div className="flex-1 min-w-0 mr-4">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold text-gradient-holographic">/{link.short_code}</span>
                        {link.title && (
                          <span className="glass px-2 py-0.5 rounded text-xs text-gray-300">
                            {link.title}
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-400 truncate">{link.original_url}</div>
                    </div>
                    <Button variant="primary" size="sm" onClick={() => handleAssignExisting(link.id)}>
                      <Plus className="w-4 h-4 mr-1" />
                      Add
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </GlassCard>
    </div>
  );
}

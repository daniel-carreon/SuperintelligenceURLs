'use client';

import { useState, useEffect } from 'react';
import { assignLinkToProject, getProjectLinks } from '@/lib/video-projects-api';
import { getAllURLs } from '@/lib/api';
import { GlassCard } from './ui/GlassCard';
import Button from './ui/Button';
import { X, Plus } from 'lucide-react';

interface AddLinksToProjectModalProps {
  projectId: string;
  projectTitle: string;
  onClose: () => void;
  onSuccess: () => void;
}

export function AddLinksToProjectModal({ projectId, projectTitle, onClose, onSuccess }: AddLinksToProjectModalProps) {
  const [availableLinks, setAvailableLinks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLinks();
  }, []);

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

  const handleAdd = async (urlId: string) => {
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
        <button onClick={onClose} className="absolute top-4 right-4 w-8 h-8 glass rounded-lg flex items-center justify-center">
          <X className="w-5 h-5" />
        </button>

        <h3 className="text-2xl font-bold text-gradient-holographic mb-6">{projectTitle}</h3>

        {loading ? (
          <div className="py-12 text-center text-gray-400">Loading...</div>
        ) : (
          <div className="space-y-3">
            {availableLinks.map((link) => (
              <div key={link.id} className="glass p-4 rounded-lg flex justify-between items-center">
                <div>
                  <div className="font-bold text-white">/{link.short_code}</div>
                  <div className="text-sm text-gray-400 truncate">{link.original_url}</div>
                </div>
                <Button variant="primary" size="sm" onClick={() => handleAdd(link.id)}>
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  );
}

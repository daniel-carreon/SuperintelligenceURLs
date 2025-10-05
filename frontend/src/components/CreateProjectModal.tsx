'use client';

import { useState } from 'react';
import { createVideoProject } from '@/lib/video-projects-api';
import { GlassCard } from './ui/GlassCard';
import Button from './ui/Button';
import { X } from 'lucide-react';

interface CreateProjectModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateProjectModal({ onClose, onSuccess }: CreateProjectModalProps) {
  const [title, setTitle] = useState('');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);
    try {
      await createVideoProject({
        title: title.trim(),
        youtube_url: youtubeUrl || undefined,
      });
      onSuccess();
    } catch (err: any) {
      alert(err.message || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <GlassCard intensity="strong" className="w-full max-w-md relative">
        <button onClick={onClose} className="absolute top-4 right-4 w-8 h-8 glass rounded-lg flex items-center justify-center">
          <X className="w-5 h-5" />
        </button>

        <h3 className="text-2xl font-bold text-gradient-holographic mb-6">Create Video Project</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Title *</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full h-12 px-4 glass rounded-lg text-white"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">YouTube URL (optional)</label>
            <input
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              className="w-full h-12 px-4 glass rounded-lg text-white"
            />
          </div>

          <div className="flex gap-3">
            <Button type="button" variant="secondary" className="flex-1" onClick={onClose}>Cancel</Button>
            <Button type="submit" variant="primary" className="flex-1" isLoading={loading}>Create</Button>
          </div>
        </form>
      </GlassCard>
    </div>
  );
}

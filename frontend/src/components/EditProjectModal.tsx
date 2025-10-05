'use client';

import { useState, useEffect } from 'react';
import { updateVideoProject } from '@/lib/video-projects-api';
import { GlassCard } from './ui/GlassCard';
import Button from './ui/Button';
import Input from './ui/Input';
import { X, Save } from 'lucide-react';

interface EditProjectModalProps {
  projectId: string;
  currentTitle: string;
  currentYoutubeUrl: string | null;
  currentDescription: string | null;
  onClose: () => void;
  onSuccess: () => void;
}

export function EditProjectModal({
  projectId,
  currentTitle,
  currentYoutubeUrl,
  currentDescription,
  onClose,
  onSuccess
}: EditProjectModalProps) {
  const [title, setTitle] = useState(currentTitle);
  const [youtubeUrl, setYoutubeUrl] = useState(currentYoutubeUrl || '');
  const [description, setDescription] = useState(currentDescription || '');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      alert('Title is required');
      return;
    }

    setLoading(true);
    try {
      await updateVideoProject(projectId, {
        title: title.trim(),
        youtube_url: youtubeUrl.trim() || null,
        description: description.trim() || null
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      alert(err.message || 'Failed to update project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <GlassCard intensity="strong" className="w-full max-w-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 glass rounded-lg flex items-center justify-center hover:glass-strong transition-all"
          disabled={loading}
        >
          <X className="w-5 h-5" />
        </button>

        <h3 className="text-2xl font-bold text-gradient-holographic mb-6">
          Edit Video Project
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Project Title *
            </label>
            <Input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter project title"
              required
              disabled={loading}
            />
          </div>

          {/* YouTube URL */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              YouTube URL (optional)
            </label>
            <Input
              type="url"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              disabled={loading}
            />
            <p className="text-xs text-gray-500 mt-1">
              Will auto-fetch thumbnail and metadata if provided
            </p>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Description (optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter project description"
              rows={3}
              disabled={loading}
              className="w-full glass rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-neon-cyan transition-all resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3 pt-4">
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              disabled={loading}
            >
              <Save className="w-4 h-4 mr-2" />
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </Button>
          </div>
        </form>
      </GlassCard>
    </div>
  );
}

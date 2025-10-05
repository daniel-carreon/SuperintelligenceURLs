'use client';

import { useState, useEffect } from 'react';
import { createVideoProject } from '@/lib/video-projects-api';
import { GlassCard } from './ui/GlassCard';
import Button from './ui/Button';
import Input from './ui/Input';
import { Youtube, Sparkles, X } from 'lucide-react';

interface CreateProjectModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateProjectModal({ onClose, onSuccess }: CreateProjectModalProps) {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [videoId, setVideoId] = useState<string | null>(null);
  const [thumbnailUrl, setThumbnailUrl] = useState<string | null>(null);

  // Extract YouTube video ID from URL
  const extractVideoId = (url: string): string | null => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
      /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
      /youtube\.com\/v\/([a-zA-Z0-9_-]{11})/,
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }
    return null;
  };

  // Auto-preview YouTube thumbnail when URL changes
  useEffect(() => {
    const id = extractVideoId(youtubeUrl);
    if (id) {
      setVideoId(id);
      setThumbnailUrl(`https://img.youtube.com/vi/${id}/maxresdefault.jpg`);
    } else {
      setVideoId(null);
      setThumbnailUrl(null);
    }
  }, [youtubeUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate: Either YouTube URL or manual title
    if (!youtubeUrl && !title.trim()) {
      setError('Please provide a YouTube URL or manual title');
      return;
    }

    setLoading(true);

    try {
      await createVideoProject({
        title: title.trim() || 'Untitled Project',
        youtube_url: youtubeUrl || undefined,
        description: description.trim() || undefined,
      });

      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Failed to create video project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <GlassCard
        intensity="strong"
        glow="cyan"
        className="w-full max-w-2xl animate-scale-in relative"
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-10 h-10 glass hover:glass-strong rounded-lg flex items-center justify-center transition-all hover:scale-110 group"
        >
          <X className="w-5 h-5 text-gray-400 group-hover:text-neon-cyan transition-colors" />
        </button>

        <div className="p-6 space-y-6">
          {/* Header */}
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 gradient-holographic rounded-xl flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gradient-holographic">
                  Create Video Project
                </h3>
                <p className="text-sm text-gray-400">
                  Organize your links by YouTube video
                </p>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* YouTube URL Input */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                <Youtube className="w-4 h-4 text-red-500" />
                YouTube URL (Optional)
              </label>
              <Input
                type="url"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1.5">
                Paste a YouTube URL to auto-fetch video metadata and thumbnail
              </p>
            </div>

            {/* Thumbnail Preview */}
            {thumbnailUrl && videoId && (
              <div className="animate-fade-in">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Preview
                </label>
                <div className="relative rounded-xl overflow-hidden border border-neon-cyan/30 group">
                  <img
                    src={thumbnailUrl}
                    alt="YouTube thumbnail"
                    className="w-full h-48 object-cover"
                    onError={(e) => {
                      // Fallback to HQ thumbnail
                      e.currentTarget.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-dark-bg via-transparent to-transparent" />
                  <div className="absolute bottom-3 left-3 glass px-3 py-1 rounded-lg text-xs font-medium text-white">
                    Video ID: {videoId}
                  </div>
                  {/* YouTube play button overlay */}
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center shadow-2xl">
                      <Youtube className="w-8 h-8 text-white" />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Manual Title Input */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Project Title {!youtubeUrl && <span className="text-red-400">*</span>}
              </label>
              <Input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={youtubeUrl ? "Auto-fetched from YouTube" : "My Video Project"}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1.5">
                {youtubeUrl
                  ? "Leave empty to auto-fetch from YouTube"
                  : "Required if no YouTube URL provided"}
              </p>
            </div>

            {/* Description (Optional) */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description (Optional)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add notes about this video project..."
                className="w-full h-24 px-4 py-3 glass rounded-lg text-white placeholder:text-gray-500 focus:glass-strong focus:outline-none focus:ring-2 focus:ring-neon-cyan/30 resize-none"
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="glass-strong border border-red-500/50 rounded-lg p-4 animate-fade-in">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t border-white/10">
              <Button
                type="button"
                variant="secondary"
                className="flex-1"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                className="flex-1"
                isLoading={loading}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Create Project
              </Button>
            </div>
          </form>
        </div>

        {/* Holographic glow effect */}
        <div className="absolute inset-0 gradient-holographic opacity-5 pointer-events-none" />
      </GlassCard>
    </div>
  );
}

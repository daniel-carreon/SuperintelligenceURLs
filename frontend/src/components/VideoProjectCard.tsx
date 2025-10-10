'use client';

import { VideoProject } from '@/lib/video-projects-api';
import { GlassCard } from './ui/GlassCard';
import { TrendingUp, Youtube, ExternalLink, Link2, Eye, Pencil, Copy, Check } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

interface VideoProjectCardProps {
  project: VideoProject;
  links?: Array<{ short_code: string; title?: string; click_count: number }>;
  onManageLinks?: () => void;
  onEdit?: () => void;
}

export function VideoProjectCard({ project, links = [], onManageLinks, onEdit }: VideoProjectCardProps) {
  const router = useRouter();
  const [copiedLink, setCopiedLink] = useState<string | null>(null);

  const handleClick = () => {
    // Navigate to project analytics page
    router.push(`/dashboard/projects/${project.id}/analytics`);
  };

  const copyToClipboard = async (shortCode: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const baseUrl = window.location.origin;
    const fullUrl = `${baseUrl}/${shortCode}`;

    try {
      await navigator.clipboard.writeText(fullUrl);
      setCopiedLink(shortCode);
      setTimeout(() => setCopiedLink(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // YouTube thumbnail fallback
  const thumbnailUrl = project.thumbnail_url || `https://img.youtube.com/vi/${project.youtube_video_id}/maxresdefault.jpg`;

  return (
    <GlassCard
      glow="cyan"
      className="group relative overflow-hidden cursor-pointer animate-fade-in hover:scale-[1.03] transition-all duration-300"
      onClick={handleClick}
    >
      {/* Thumbnail Background with Gradient Overlay */}
      <div className="relative h-48 w-full rounded-xl overflow-hidden mb-4">
        {project.youtube_video_id || project.thumbnail_url ? (
          <div className="relative w-full h-full">
            <img
              src={thumbnailUrl}
              alt={project.title}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              onError={(e) => {
                // Fallback to default YouTube thumbnail on error
                e.currentTarget.src = `https://img.youtube.com/vi/${project.youtube_video_id}/hqdefault.jpg`;
              }}
            />
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-dark-bg via-dark-bg/60 to-transparent" />
          </div>
        ) : (
          // Fallback for projects without YouTube URL
          <div className="w-full h-full gradient-holographic flex items-center justify-center opacity-20">
            <Link2 className="w-16 h-16 text-white" />
          </div>
        )}

        {/* Hover overlay with "View Analytics" */}
        <div className="absolute inset-0 bg-neon-cyan/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-sm">
          <div className="glass-strong px-6 py-3 rounded-full flex items-center gap-2">
            <Eye className="w-5 h-5 text-neon-cyan" />
            <span className="text-sm font-semibold text-white">View Analytics</span>
          </div>
        </div>
      </div>

      {/* Title */}
      <h3 className="text-xl font-bold text-gradient-holographic mb-3 line-clamp-2 group-hover:text-neon-cyan transition-colors">
        {project.title}
      </h3>

      {/* Stats Row */}
      <div className="flex items-center gap-4 mb-4">
        {/* Total Clicks */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 gradient-holographic rounded-lg flex items-center justify-center">
            <TrendingUp className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="text-2xl font-black text-neon-cyan">
              {project.total_clicks || 0}
            </div>
            <div className="text-xs text-gray-500">clicks</div>
          </div>
        </div>

        <div className="h-10 w-px bg-white/10" />

        {/* Total Links */}
        <div>
          <div className="text-lg font-bold text-white">
            {project.total_links || links.length || 0}
          </div>
          <div className="text-xs text-gray-500">links</div>
        </div>

        {/* Unique Visitors */}
        {project.unique_visitors !== undefined && project.unique_visitors > 0 && (
          <>
            <div className="h-10 w-px bg-white/10" />
            <div>
              <div className="text-lg font-bold text-neon-purple">
                {project.unique_visitors}
              </div>
              <div className="text-xs text-gray-500">visitors</div>
            </div>
          </>
        )}
      </div>

      {/* Links Pills (Preview) */}
      {links.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Links in this project
          </div>
          <div className="flex flex-wrap gap-2">
            {links.slice(0, 3).map((link, idx) => (
              <div
                key={link.short_code}
                className="glass px-3 py-1.5 rounded-full text-xs font-medium text-white border border-white/10 flex items-center gap-2 animate-fade-in group/pill hover:glass-strong transition-all"
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                <div className="w-1.5 h-1.5 rounded-full bg-neon-cyan animate-pulse" />
                <span
                  className="cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    router.push(`/dashboard/analytics?code=${link.short_code}`);
                  }}
                >
                  /{link.short_code}
                </span>
                <span className="text-neon-cyan font-bold">{link.click_count}</span>
                <button
                  onClick={(e) => copyToClipboard(link.short_code, e)}
                  className="ml-1 hover:scale-110 transition-transform"
                  title="Copy link"
                >
                  {copiedLink === link.short_code ? (
                    <Check className="w-3 h-3 text-green-400" />
                  ) : (
                    <Copy className="w-3 h-3 text-gray-400 group-hover/pill:text-neon-cyan transition-colors" />
                  )}
                </button>
              </div>
            ))}
            {links.length > 3 && (
              <div className="glass px-3 py-1.5 rounded-full text-xs font-medium text-gray-400 border border-white/10">
                +{links.length - 3} more
              </div>
            )}
          </div>
        </div>
      )}

      {/* Add Links Button (Empty State) */}
      {links.length === 0 && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onManageLinks?.();
          }}
          className="w-full mt-2 glass hover:glass-strong border border-dashed border-neon-cyan/30 hover:border-neon-cyan/50 rounded-lg py-3 text-sm font-medium text-gray-400 hover:text-neon-cyan transition-colors flex items-center justify-center gap-2"
        >
          <Link2 className="w-4 h-4" />
          Add Links to Project
        </button>
      )}

      {/* Action Buttons - Bottom Right */}
      <div className="mt-4 flex items-center justify-end gap-2">
        {/* Edit Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onEdit?.();
          }}
          className="glass hover:glass-strong px-3 py-2 rounded-lg flex items-center gap-2 text-xs font-medium text-gray-400 hover:text-neon-cyan transition-all hover:scale-105"
          title="Edit project"
        >
          <Pencil className="w-4 h-4" />
          <span>Edit</span>
        </button>

        {/* YouTube Link Button */}
        {project.youtube_url && (
          <a
            href={project.youtube_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="glass hover:glass-strong px-3 py-2 rounded-lg flex items-center gap-2 text-xs font-medium text-gray-400 hover:text-red-500 transition-all hover:scale-105 group/youtube"
          >
            <Youtube className="w-4 h-4" />
            <span>YouTube</span>
            <ExternalLink className="w-3 h-3 group-hover/youtube:translate-x-0.5 transition-transform" />
          </a>
        )}
      </div>

      {/* Holographic glow effect on hover */}
      <div className="absolute inset-0 gradient-holographic opacity-0 group-hover:opacity-5 transition-opacity duration-300 pointer-events-none" />
    </GlassCard>
  );
}

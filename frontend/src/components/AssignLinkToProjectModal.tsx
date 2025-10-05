'use client';

import { useState, useEffect } from 'react';
import { assignLinkToProject } from '@/lib/video-projects-api';
import { getAllVideoProjects } from '@/lib/video-projects-api';
import { GlassCard } from './ui/GlassCard';
import Button from './ui/Button';
import { X, Plus, Video } from 'lucide-react';

interface AssignLinkToProjectModalProps {
  urlId: string;
  urlTitle: string;
  shortCode: string;
  onClose: () => void;
  onSuccess: () => void;
}

export function AssignLinkToProjectModal({
  urlId,
  urlTitle,
  shortCode,
  onClose,
  onSuccess
}: AssignLinkToProjectModalProps) {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const allProjects = await getAllVideoProjects();
      setProjects(allProjects);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssign = async (projectId: string) => {
    try {
      await assignLinkToProject(urlId, projectId);
      onSuccess();
      onClose();
    } catch (err: any) {
      alert(err.message || 'Failed to assign link to project');
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <GlassCard intensity="strong" className="w-full max-w-2xl relative max-h-[80vh] overflow-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 glass rounded-lg flex items-center justify-center hover:glass-strong transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="mb-6">
          <h3 className="text-2xl font-bold text-gradient-holographic mb-2">
            Assign to Project
          </h3>
          <div className="glass p-3 rounded-lg">
            <div className="font-mono text-sm text-neon-cyan">/{shortCode}</div>
            <div className="text-sm text-gray-400 truncate">{urlTitle || 'Untitled link'}</div>
          </div>
        </div>

        {loading ? (
          <div className="py-12 text-center text-gray-400">
            <div className="w-12 h-12 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            Loading projects...
          </div>
        ) : projects.length === 0 ? (
          <div className="py-12 text-center">
            <div className="w-16 h-16 gradient-holographic rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Video className="w-8 h-8 text-white" />
            </div>
            <p className="text-gray-400 mb-6">No video projects yet</p>
            <Button variant="primary" onClick={onClose}>
              Create Project First
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {projects.map((project) => (
              <div
                key={project.id}
                className="glass p-4 rounded-lg hover:glass-strong transition-all group cursor-pointer"
                onClick={() => handleAssign(project.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    {project.thumbnail_url ? (
                      <img
                        src={project.thumbnail_url}
                        alt={project.title}
                        className="w-16 h-10 object-cover rounded-md flex-shrink-0"
                      />
                    ) : (
                      <div className="w-16 h-10 gradient-holographic rounded-md flex items-center justify-center flex-shrink-0">
                        <Video className="w-6 h-6 text-white" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="font-bold text-white truncate">{project.title}</div>
                      <div className="text-xs text-gray-400">
                        {project.total_links || 0} links · {project.total_clicks || 0} clicks
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAssign(project.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  );
}

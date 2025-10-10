'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getAllVideoProjects, getProjectLinks, deleteVideoProject, type VideoProject } from '@/lib/video-projects-api';
import { logout } from '@/lib/auth';
import { GlassCard } from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import { VideoProjectCard } from '@/components/VideoProjectCard';
import { CreateProjectModal } from '@/components/CreateProjectModal';
import { AddLinksToProjectModal } from '@/components/AddLinksToProjectModal';
import { EditProjectModal } from '@/components/EditProjectModal';
import { Sparkles, Plus, Video, LogOut, Trash2, Link2 } from 'lucide-react';
import Link from 'next/link';

export default function VideoProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<VideoProject[]>([]);
  const [projectLinks, setProjectLinks] = useState<Record<string, any[]>>({});
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [managingProject, setManagingProject] = useState<VideoProject | null>(null);
  const [editingProject, setEditingProject] = useState<VideoProject | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      console.log('🚀 [DEBUG] Starting to load projects...');
      setLoading(true);

      console.log('🌐 [DEBUG] Calling getAllVideoProjects()...');
      const data = await getAllVideoProjects();
      console.log('✅ [DEBUG] Received projects:', data.length, 'projects');
      setProjects(data);

      // Load links for each project
      console.log('🔗 [DEBUG] Loading links for each project...');
      const linksMap: Record<string, any[]> = {};
      await Promise.all(
        data.map(async (project) => {
          try {
            console.log(`  📎 [DEBUG] Loading links for project ${project.id}...`);
            const links = await getProjectLinks(project.id);
            console.log(`  ✅ [DEBUG] Got ${links.length} links for project ${project.id}`);
            linksMap[project.id] = links;
          } catch (error) {
            console.error(`❌ [DEBUG] Failed to load links for project ${project.id}:`, error);
            linksMap[project.id] = [];
          }
        })
      );
      console.log('✅ [DEBUG] All links loaded successfully');
      setProjectLinks(linksMap);
    } catch (error) {
      console.error('❌ [DEBUG] Failed to load projects:', error);
    } finally {
      console.log('🏁 [DEBUG] Finished loading, setting loading to false');
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const handleDeleteProject = async (projectId: string) => {
    if (!confirm('⚠️ Delete this video project?\n\nAll links will be unassigned (but not deleted). This cannot be undone.')) {
      return;
    }

    try {
      await deleteVideoProject(projectId);
      await loadProjects();
    } catch (error: any) {
      alert(error.message || 'Failed to delete project');
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg relative overflow-hidden">
      {/* Animated mesh background */}
      <div className="fixed inset-0 bg-gradient-mesh opacity-60 animate-pulse" style={{ animationDuration: '8s' }} />

      {/* Floating orbs */}
      <div className="fixed top-20 left-10 w-72 h-72 bg-neon-cyan rounded-full opacity-20 blur-3xl animate-float" />
      <div className="fixed bottom-20 right-10 w-96 h-96 bg-neon-purple rounded-full opacity-20 blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      <div className="fixed top-1/2 left-1/2 w-80 h-80 bg-neon-pink rounded-full opacity-15 blur-3xl animate-float" style={{ animationDelay: '4s' }} />

      <div className="relative z-10">
        {/* Header */}
        <nav className="glass-strong border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-20">
              <div className="flex items-center gap-3 group">
                <div className="w-10 h-10 gradient-holographic rounded-xl flex items-center justify-center transform group-hover:rotate-180 transition-transform duration-500">
                  <Video className="w-6 h-6 text-white" />
                </div>
                <div>
                  <span className="text-2xl font-bold text-gradient-holographic block">
                    My Video Projects
                  </span>
                  <span className="text-xs text-gray-400">Organize links by video</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Link href="/dashboard/links">
                  <Button variant="secondary">
                    <Link2 className="w-4 h-4 mr-2" />
                    All Links
                  </Button>
                </Link>
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
                Video Projects Dashboard
              </span>
            </div>
            <h1 className="text-5xl font-black text-gradient-holographic mb-4">
              Your Video Projects
            </h1>
            <p className="text-gray-400 text-lg max-w-3xl">
              Organize your short links by YouTube videos. Track aggregated analytics across all links in each project.
            </p>
          </div>

          {/* Create Project Button */}
          <div className="mb-8">
            <Button
              variant="primary"
              size="lg"
              onClick={() => setShowCreateModal(true)}
              className="px-8"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create Video Project
            </Button>
          </div>

          {/* Projects Grid */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <div className="w-16 h-16 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-gray-400">Loading your projects...</p>
              </div>
            </div>
          ) : projects.length === 0 ? (
            <GlassCard intensity="strong" className="text-center py-20 relative overflow-hidden">
              <div className="absolute inset-0 gradient-holographic opacity-5" />
              <div className="relative z-10">
                <div className="w-24 h-24 gradient-holographic rounded-3xl flex items-center justify-center mx-auto mb-8 animate-float">
                  <Video className="w-12 h-12 text-white" />
                </div>
                <h3 className="text-3xl font-black text-gradient-holographic mb-4">
                  No projects yet
                </h3>
                <p className="text-gray-400 text-lg mb-8 max-w-md mx-auto">
                  Create your first video project to organize links by YouTube video
                </p>
                <Button
                  variant="primary"
                  size="lg"
                  onClick={() => setShowCreateModal(true)}
                  className="px-8"
                >
                  <Sparkles className="w-5 h-5 mr-2" />
                  Create Your First Project
                </Button>
              </div>
            </GlassCard>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project, idx) => (
                <div key={project.id} className="relative group" style={{ animationDelay: `${idx * 100}ms` }}>
                  <VideoProjectCard
                    project={project}
                    links={projectLinks[project.id] || []}
                    onManageLinks={() => setManagingProject(project)}
                    onEdit={() => setEditingProject(project)}
                  />

                  {/* Delete button (hidden, shown on hover) */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteProject(project.id);
                    }}
                    className="absolute top-4 right-4 w-8 h-8 bg-red-500/20 hover:bg-red-500/40 text-red-400 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all z-10"
                    title="Delete project"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {showCreateModal && (
        <CreateProjectModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            loadProjects();
          }}
        />
      )}

      {managingProject && (
        <AddLinksToProjectModal
          projectId={managingProject.id}
          projectTitle={managingProject.title}
          onClose={() => setManagingProject(null)}
          onSuccess={() => {
            loadProjects();
          }}
        />
      )}

      {editingProject && (
        <EditProjectModal
          projectId={editingProject.id}
          currentTitle={editingProject.title}
          currentYoutubeUrl={editingProject.youtube_url || null}
          currentDescription={editingProject.description || null}
          onClose={() => setEditingProject(null)}
          onSuccess={() => {
            setEditingProject(null);
            loadProjects();
          }}
        />
      )}
    </div>
  );
}

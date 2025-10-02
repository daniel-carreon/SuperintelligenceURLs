'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getFolderTree, createFolder, updateFolder, type Folder } from '@/lib/folders-api';
import { logout } from '@/lib/auth';
import { GlassCard } from './ui/GlassCard';
import Button from './ui/Button';
import { HexColorPicker } from './ui/HexColorPicker';
import { FolderPlus, ChevronDown, ChevronRight, Pencil, LogOut } from 'lucide-react';

interface FoldersSidebarProps {
  selectedFolder?: string | null;
  onSelectFolder?: (folderId: string | null) => void;
}

export default function FoldersSidebar({ selectedFolder, onSelectFolder }: FoldersSidebarProps) {
  const router = useRouter();
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingFolder, setEditingFolder] = useState<Folder | null>(null);

  useEffect(() => {
    loadFolders();
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const loadFolders = async () => {
    try {
      const data = await getFolderTree();
      setFolders(data.folders);
    } catch (error) {
      console.error('Failed to load folders:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleFolder = (folderId: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
    } else {
      newExpanded.add(folderId);
    }
    setExpandedFolders(newExpanded);
  };

  const renderFolder = (folder: Folder, level: number = 0) => {
    const hasSubfolders = folder.subfolders && folder.subfolders.length > 0;
    const isExpanded = expandedFolders.has(folder.id);

    return (
      <div key={folder.id} style={{ marginLeft: `${level * 16}px` }}>
        <div
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors group cursor-pointer ${
            selectedFolder === folder.id ? 'bg-neon-cyan/20 border border-neon-cyan/50' : 'hover:bg-white/5'
          }`}
          onClick={() => onSelectFolder?.(folder.id)}
        >
          {hasSubfolders && (
            <button
              className="text-gray-400 hover:text-white transition-colors"
              onClick={() => toggleFolder(folder.id)}
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
          )}
          <span className="text-xl">{folder.icon}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: folder.color }}
              />
              <span className="text-sm font-medium text-white truncate">
                {folder.name}
              </span>
            </div>
          </div>
          {folder.link_count !== undefined && folder.link_count > 0 && (
            <span className="text-xs font-semibold text-neon-cyan px-2 py-1 glass rounded-lg">
              {folder.link_count}
            </span>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setEditingFolder(folder);
            }}
            className="opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-neon-cyan"
            title="Edit folder"
          >
            <Pencil className="w-3.5 h-3.5" />
          </button>
        </div>

        {hasSubfolders && isExpanded && (
          <div className="ml-2 border-l border-white/10 pl-2 mt-1">
            {folder.subfolders!.map((subfolder) =>
              renderFolder(subfolder, level + 1)
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      <div className="w-80 h-screen fixed left-0 top-0 p-4 overflow-y-auto">
        <GlassCard intensity="strong" className="h-full">
          <div className="p-4 space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gradient-holographic">
                  Folders
                </h2>
                <p className="text-xs text-gray-400">Organize your links</p>
              </div>
            </div>

            {/* All Links Button */}
            <Button
              variant={selectedFolder === null ? 'primary' : 'secondary'}
              size="sm"
              className="w-full mb-3"
              onClick={() => onSelectFolder?.(null)}
            >
              All Links
            </Button>

            {/* New Folder Button */}
            <Button
              variant="primary"
              size="sm"
              className="w-full"
              onClick={() => setShowCreateModal(true)}
            >
              <FolderPlus className="w-4 h-4 mr-2" />
              New Folder
            </Button>

            {/* Folders List */}
            <div className="space-y-1 mt-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="w-8 h-8 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin mx-auto" />
                  <p className="text-sm text-gray-400 mt-2">Loading folders...</p>
                </div>
              ) : folders.length === 0 ? (
                <div className="text-center py-8">
                  <span className="text-4xl">📁</span>
                  <p className="text-sm text-gray-400 mt-2">No folders yet</p>
                  <p className="text-xs text-gray-500">Create your first folder</p>
                </div>
              ) : (
                folders.map((folder) => renderFolder(folder))
              )}
            </div>

            {/* Logout Button */}
            <div className="pt-4 mt-4 border-t border-white/10">
              <Button
                variant="secondary"
                size="sm"
                className="w-full"
                onClick={handleLogout}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Create Folder Modal - OUTSIDE sidebar */}
      {showCreateModal && (
        <CreateFolderModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            loadFolders();
            setShowCreateModal(false);
          }}
        />
      )}

      {/* Edit Folder Modal - OUTSIDE sidebar */}
      {editingFolder && (
        <EditFolderModal
          folder={editingFolder}
          onClose={() => setEditingFolder(null)}
          onSuccess={() => {
            loadFolders();
            setEditingFolder(null);
          }}
        />
      )}
    </>
  );
}

// Simplified Create Folder Modal - Minimal UI
function CreateFolderModal({
  onClose,
  onSuccess,
}: {
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [name, setName] = useState('');
  const [color, setColor] = useState('#00fff5');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    try {
      await createFolder({ name: name.trim(), color, icon: '📁' });
      onSuccess();
    } catch (error) {
      console.error('Failed to create folder:', error);
      alert('Failed to create folder');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <GlassCard
        intensity="strong"
        glow="cyan"
        className="w-full max-w-md animate-scale-in relative z-[101]"
      >
        <div className="p-6 space-y-5">
          <div>
            <h3 className="text-2xl font-bold text-gradient-holographic mb-2">
              Create Folder
            </h3>
            <p className="text-sm text-gray-400">
              Organize your links by category
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name Input */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Folder Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My Folder"
                className="w-full h-12 px-4 glass rounded-lg text-white placeholder:text-gray-500 focus:glass-strong focus:outline-none focus:ring-2 focus:ring-neon-cyan/30"
                required
                autoFocus
              />
            </div>

            {/* Hex Color Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Color
              </label>
              <HexColorPicker value={color} onChange={setColor} />
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="secondary"
                className="flex-1"
                onClick={onClose}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                className="flex-1"
                isLoading={loading}
              >
                Create Folder
              </Button>
            </div>
          </form>
        </div>
      </GlassCard>
    </div>
  );
}

// Simplified Edit Folder Modal - Minimal UI
function EditFolderModal({
  folder,
  onClose,
  onSuccess,
}: {
  folder: Folder;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [name, setName] = useState(folder.name);
  const [color, setColor] = useState(folder.color);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    try {
      await updateFolder(folder.id, {
        name: name.trim(),
        color,
        icon: folder.icon, // Keep existing icon
      });
      onSuccess();
    } catch (error) {
      console.error('Failed to update folder:', error);
      alert('Failed to update folder');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`⚠️ Delete folder "${folder.name}"?\n\nAll links in this folder will also be deleted. This cannot be undone.`)) {
      return;
    }

    setLoading(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/folders/${folder.id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Failed to delete folder');
      }

      alert('Folder deleted successfully!');
      onSuccess();
    } catch (error) {
      console.error('Failed to delete folder:', error);
      alert('Failed to delete folder');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <GlassCard
        intensity="strong"
        glow="cyan"
        className="w-full max-w-md animate-scale-in relative z-[101]"
      >
        <div className="p-6 space-y-5">
          <div>
            <h3 className="text-2xl font-bold text-gradient-holographic mb-2">
              Edit Folder
            </h3>
            <p className="text-sm text-gray-400">
              Update folder name or color
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name Input */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Folder Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My Folder"
                className="w-full h-12 px-4 glass rounded-lg text-white placeholder:text-gray-500 focus:glass-strong focus:outline-none focus:ring-2 focus:ring-neon-cyan/30"
                required
                autoFocus
              />
            </div>

            {/* Hex Color Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Color
              </label>
              <HexColorPicker value={color} onChange={setColor} />
            </div>

            {/* Delete Warning */}
            <div className="border-t border-white/10 pt-4">
              <p className="text-xs text-gray-500 mb-3">
                Danger Zone: Deleting this folder will remove all links assigned to it.
              </p>
              <Button
                type="button"
                variant="danger"
                className="w-full"
                onClick={handleDelete}
                isLoading={loading}
              >
                Delete Folder
              </Button>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <Button
                type="button"
                variant="secondary"
                className="flex-1"
                onClick={onClose}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                className="flex-1"
                isLoading={loading}
              >
                Save Changes
              </Button>
            </div>
          </form>
        </div>
      </GlassCard>
    </div>
  );
}
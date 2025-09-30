'use client';

import { useState, useEffect } from 'react';
import { getFolderTree, createFolder, updateFolder, type Folder } from '@/lib/folders-api';
import { GlassCard } from './ui/GlassCard';
import Button from './ui/Button';
import { FolderPlus, ChevronDown, ChevronRight, Pencil } from 'lucide-react';

export default function FoldersSidebar() {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingFolder, setEditingFolder] = useState<Folder | null>(null);

  useEffect(() => {
    loadFolders();
  }, []);

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
          className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/5 transition-colors group"
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
      <div className="w-72 h-screen fixed left-0 top-0 p-4 overflow-y-auto">
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

// Simple Create Folder Modal
function CreateFolderModal({
  onClose,
  onSuccess,
}: {
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [name, setName] = useState('');
  const [color, setColor] = useState('#00fff5');
  const [icon, setIcon] = useState('📁');
  const [loading, setLoading] = useState(false);

  const colors = [
    { name: 'Cyan', value: '#00fff5' },
    { name: 'Blue', value: '#0066ff' },
    { name: 'Purple', value: '#8b5cf6' },
    { name: 'Pink', value: '#ff006e' },
    { name: 'Orange', value: '#ff6b35' },
    { name: 'Green', value: '#10b981' },
  ];

  const icons = ['📁', '👥', '💎', '💼', '🎥', '🎬', '🎙️', '📚', '💻', '🚀'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    try {
      await createFolder({ name: name.trim(), color, icon });
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
        <div className="p-6 space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-gradient-holographic mb-2">
              Create Folder
            </h3>
            <p className="text-sm text-gray-400">
              Organize your links by category
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
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
              />
            </div>

            {/* Icon Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Icon
              </label>
              <div className="grid grid-cols-5 gap-2">
                {icons.map((emoji) => (
                  <button
                    key={emoji}
                    type="button"
                    onClick={() => setIcon(emoji)}
                    className={`p-3 rounded-lg text-2xl transition-all ${
                      icon === emoji
                        ? 'glass-strong ring-2 ring-neon-cyan scale-110'
                        : 'glass hover:glass-strong'
                    }`}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>

            {/* Color Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Color
              </label>
              <div className="grid grid-cols-3 gap-2">
                {colors.map((c) => (
                  <button
                    key={c.value}
                    type="button"
                    onClick={() => setColor(c.value)}
                    className={`p-3 rounded-lg transition-all ${
                      color === c.value
                        ? 'glass-strong ring-2 ring-white scale-105'
                        : 'glass hover:glass-strong'
                    }`}
                    style={{ backgroundColor: c.value }}
                  >
                    <span className="text-xs font-semibold text-white">
                      {c.name}
                    </span>
                  </button>
                ))}
              </div>
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

// Edit Folder Modal
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
  const [icon, setIcon] = useState(folder.icon);
  const [loading, setLoading] = useState(false);

  const colors = [
    { name: 'Cyan', value: '#00fff5' },
    { name: 'Blue', value: '#0066ff' },
    { name: 'Purple', value: '#8b5cf6' },
    { name: 'Pink', value: '#ff006e' },
    { name: 'Orange', value: '#ff6b35' },
    { name: 'Green', value: '#10b981' },
  ];

  const icons = ['📁', '👥', '💎', '💼', '🎥', '🎬', '🎙️', '📚', '💻', '🚀'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    try {
      await updateFolder(folder.id, {
        name: name.trim(),
        color,
        icon,
      });
      onSuccess();
    } catch (error) {
      console.error('Failed to update folder:', error);
      alert('Failed to update folder');
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
        <div className="p-6 space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-gradient-holographic mb-2">
              Edit Folder
            </h3>
            <p className="text-sm text-gray-400">
              Update folder name, color, or icon
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
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
              />
            </div>

            {/* Icon Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Icon
              </label>
              <div className="grid grid-cols-5 gap-2">
                {icons.map((emoji) => (
                  <button
                    key={emoji}
                    type="button"
                    onClick={() => setIcon(emoji)}
                    className={`p-3 rounded-lg text-2xl transition-all ${
                      icon === emoji
                        ? 'glass-strong ring-2 ring-neon-cyan scale-110'
                        : 'glass hover:glass-strong'
                    }`}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>

            {/* Color Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Color
              </label>
              <div className="grid grid-cols-3 gap-2">
                {colors.map((c) => (
                  <button
                    key={c.value}
                    type="button"
                    onClick={() => setColor(c.value)}
                    className={`p-3 rounded-lg transition-all ${
                      color === c.value
                        ? 'glass-strong ring-2 ring-white scale-105'
                        : 'glass hover:glass-strong'
                    }`}
                    style={{ backgroundColor: c.value }}
                  >
                    <span className="text-xs font-semibold text-white">
                      {c.name}
                    </span>
                  </button>
                ))}
              </div>
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
                Save Changes
              </Button>
            </div>
          </form>
        </div>
      </GlassCard>
    </div>
  );
}
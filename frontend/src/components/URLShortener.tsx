'use client';

import { useState, useEffect } from 'react';
import { createShortURL, URLResponse } from '@/lib/api';
import { getAllFolders, type Folder } from '@/lib/folders-api';
import Button from './ui/Button';
import Input from './ui/Input';
import { Copy, Check, ExternalLink, BarChart3, FolderInput } from 'lucide-react';
import Link from 'next/link';

export default function URLShortener() {
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [folderId, setFolderId] = useState<string>('');
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<URLResponse | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadFolders();
  }, []);

  const loadFolders = async () => {
    try {
      const data = await getAllFolders();
      setFolders(data);
    } catch (error) {
      console.error('Failed to load folders:', error);
    }
  };

  const validateURL = (url: string): boolean => {
    try {
      const urlObj = new URL(url);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResult(null);

    if (!url) {
      setError('Please enter a URL');
      return;
    }

    if (!validateURL(url)) {
      setError('Please enter a valid URL (must start with http:// or https://)');
      return;
    }

    setLoading(true);

    try {
      const response = await createShortURL({
        original_url: url,
        title: title || undefined,
        folder_id: folderId || undefined,
      });
      setResult(response);
      setUrl('');
      setTitle('');
      setFolderId('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to shorten URL. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!result) return;
    const shortURL = `${window.location.origin}/${result.short_code}`;
    await navigator.clipboard.writeText(shortURL);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6">
      {/* Main Form */}
      <div className="glass-strong rounded-2xl p-8 border border-white/10 glow-cyan animate-fade-in">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              type="url"
              placeholder="https://example.com/your-long-url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              error={error}
              label="Enter your long URL"
              disabled={loading}
            />
          </div>

          <div>
            <Input
              type="text"
              placeholder="My awesome link (optional)"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              label="Title (optional)"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
              <FolderInput className="w-4 h-4" />
              Assign to Folder (optional)
            </label>
            <select
              value={folderId}
              onChange={(e) => setFolderId(e.target.value)}
              disabled={loading}
              className="w-full h-12 px-4 glass rounded-lg text-white bg-dark-bg/50 border border-white/10 focus:glass-strong focus:outline-none focus:ring-2 focus:ring-neon-cyan/30 transition-all"
            >
              <option value="">No folder (All Links)</option>
              {folders.map((folder) => (
                <option key={folder.id} value={folder.id}>
                  {folder.icon} {folder.name}
                </option>
              ))}
            </select>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full text-lg font-semibold py-4"
            isLoading={loading}
          >
            {loading ? 'Processing with AI...' : 'Shorten URL →'}
          </Button>
        </form>
      </div>

      {/* Result Card */}
      {result && (
        <div className="glass-strong rounded-2xl p-8 border border-neon-cyan/30 glow-cyan animate-slide-up relative overflow-hidden">
          <div className="absolute inset-0 gradient-holographic opacity-5" />
          <div className="space-y-6 relative z-10">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-3">
                  <span className="w-2 h-2 rounded-full bg-neon-cyan animate-pulse" />
                  <span className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Your shortened URL</span>
                </div>
                <a
                  href={`/${result.short_code}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-2xl font-black text-gradient-holographic hover:scale-105 transition-transform inline-flex items-center gap-3 break-all"
                >
                  {window.location.origin}/{result.short_code}
                  <ExternalLink className="w-6 h-6 flex-shrink-0" />
                </a>
              </div>
            </div>

            {result.title && (
              <div className="glass rounded-xl p-4 border border-white/10">
                <p className="text-xs font-semibold text-gray-400 mb-1">Title</p>
                <p className="text-base text-white font-medium">{result.title}</p>
              </div>
            )}

            <div className="glass rounded-xl p-4 border border-white/10">
              <p className="text-xs font-semibold text-gray-400 mb-1">Original URL</p>
              <p className="text-sm text-gray-300 break-all">{result.original_url}</p>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                onClick={handleCopy}
                variant="primary"
                className="flex-1 text-base font-semibold"
                size="lg"
              >
                {copied ? (
                  <>
                    <Check className="w-5 h-5 mr-2" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-5 h-5 mr-2" />
                    Copy Link
                  </>
                )}
              </Button>

              <Link href={`/dashboard/analytics?code=${result.short_code}`}>
                <Button variant="secondary" size="lg" className="flex items-center gap-2 font-semibold">
                  <BarChart3 className="w-5 h-5" />
                  View Analytics
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
'use client';

import { useEffect } from 'react';
import { use } from 'react';

export default function RedirectPage({ params }: { params: Promise<{ shortCode: string }> }) {
  const { shortCode } = use(params);

  useEffect(() => {
    // Redirect to backend for tracking
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    window.location.href = `${API_URL}/${shortCode}`;
  }, [shortCode]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Redirecting...</p>
      </div>
    </div>
  );
}
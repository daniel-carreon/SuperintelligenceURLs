'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * AuthGuard component - protects routes from unauthenticated access
 * Redirects to /login if user is not authenticated
 *
 * Uses mounted state to prevent SSR/hydration mismatch issues
 */
export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  // Set mounted to true after component mounts on client
  useEffect(() => {
    setMounted(true);
  }, []);

  // Check authentication only after component is mounted
  useEffect(() => {
    if (mounted && !isAuthenticated()) {
      router.push('/login');
    }
  }, [mounted, router]);

  // Show loading state during SSR and initial client render
  // This prevents hydration mismatch errors
  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-purple-950/30 to-black">
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  // After mounted, check authentication
  if (!isAuthenticated()) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-purple-950/30 to-black">
        <div className="text-gray-400">Redirecting to login...</div>
      </div>
    );
  }

  // If authenticated, render children
  return <>{children}</>;
}

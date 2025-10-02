'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * AuthGuard component - protects routes from unauthenticated access
 * Redirects to /login if user is not authenticated
 */
export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  // If not authenticated, show nothing while redirecting
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

import { cn } from '@/utils/cn';
import { HTMLAttributes, ReactNode } from 'react';

export interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  intensity?: 'light' | 'medium' | 'strong';
  glow?: 'cyan' | 'purple' | 'pink' | 'none';
  animate?: boolean;
}

export function GlassCard({
  className,
  children,
  intensity = 'medium',
  glow = 'none',
  animate = true,
  ...props
}: GlassCardProps) {
  const intensityClasses = {
    light: 'glass',
    medium: 'glass',
    strong: 'glass-strong',
  };

  const glowClasses = {
    cyan: 'glow-cyan',
    purple: 'glow-purple',
    pink: 'glow-pink',
    none: '',
  };

  return (
    <div
      className={cn(
        'rounded-2xl p-6',
        intensityClasses[intensity],
        glowClasses[glow],
        animate && 'transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
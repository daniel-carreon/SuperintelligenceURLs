import { cn } from '@/utils/cn';
import { InputHTMLAttributes, forwardRef } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, label, type = 'text', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            {label}
          </label>
        )}
        <input
          type={type}
          className={cn(
            'flex h-14 w-full rounded-xl glass px-6 py-4 text-base text-white',
            'placeholder:text-gray-500',
            'focus:glass-strong focus:outline-none focus:ring-2 focus:ring-neon-cyan/30 focus:glow-cyan',
            'disabled:cursor-not-allowed disabled:opacity-50',
            'transition-all duration-300',
            'border border-white/10 hover:border-white/20',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-500/30',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
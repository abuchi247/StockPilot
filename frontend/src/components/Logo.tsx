/**
 * Logo — Inventzo brand mark + optional wordmark.
 *
 * Renders an inline SVG icon (three stacked inventory bars forming an "I"
 * monogram) so it stays crisp at any size with no network request, plus an
 * optional gradient "Inventzo" wordmark next to it.
 *
 * Usage:
 *   <Logo />                       // mark + wordmark, default size
 *   <Logo showWordmark={false} />  // just the mark
 *   <Logo size={40} wordmarkClassName="from-[#818cf8] to-[#c4b5fd]" />
 */

import { cn } from '@/lib/utils';

interface LogoProps {
  /** Pixel size of the square mark. Defaults to 32. */
  size?: number;
  /** Show the "Inventzo" text next to the mark. Defaults to true. */
  showWordmark?: boolean;
  /** Extra classes on the outer wrapper. */
  className?: string;
  /**
   * Tailwind gradient classes for the wordmark text (used with bg-clip-text).
   * Defaults to the brand purple gradient suited to a light background.
   */
  wordmarkClassName?: string;
}

export function Logo({
  size = 32,
  showWordmark = true,
  className,
  wordmarkClassName = 'from-[#667eea] to-[#764ba2]',
}: LogoProps) {
  // Stable gradient id so multiple Logo instances don't collide.
  const gradientId = 'inventzo-mark-grad';

  return (
    <div className={cn('flex items-center gap-2.5', className)}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-label="Inventzo"
        className="shrink-0"
      >
        <defs>
          <linearGradient
            id={gradientId}
            x1="0"
            y1="0"
            x2="64"
            y2="64"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#667EEA" />
            <stop offset="1" stopColor="#764BA2" />
          </linearGradient>
        </defs>
        <rect width="64" height="64" rx="14" fill={`url(#${gradientId})`} />
        <rect x="18" y="16" width="28" height="8" rx="2.5" fill="#FFFFFF" />
        <rect
          x="24"
          y="28"
          width="16"
          height="8"
          rx="2.5"
          fill="#FFFFFF"
          fillOpacity="0.92"
        />
        <rect x="18" y="40" width="28" height="8" rx="2.5" fill="#FFFFFF" />
      </svg>

      {showWordmark && (
        <span
          className={cn(
            'font-extrabold tracking-tight bg-gradient-to-r bg-clip-text text-transparent',
            wordmarkClassName
          )}
          style={{ fontSize: size * 0.68, lineHeight: 1 }}
        >
          Inventzo
        </span>
      )}
    </div>
  );
}

/**
 * Auth Layout
 *
 * Clean centered card layout for authentication pages.
 * Used for login, password reset, and other unauthenticated pages.
 */

import { Logo } from '@/components/Logo';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-page px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-6 animate-fade-in">
        {/* Branding */}
        <div className="flex flex-col items-center text-center">
          <Logo size={48} />
          <p className="mt-2 text-sm text-[#666]">
            Inventory &amp; Sales ERP
          </p>
        </div>

        {/* Card */}
        <div className="rounded-xl bg-white px-5 py-6 sm:px-8 sm:py-8 shadow-[0_20px_60px_rgba(0,0,0,0.1)]">
          {children}
        </div>
      </div>
    </div>
  );
}

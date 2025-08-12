// apps/phoenix-website/app/page.tsx
'use client';

import HeroSection from '@/components/sections/HeroSection';
import EcosystemSection from '@/components/sections/EcosystemSection';
import CTASection from '@/components/sections/CTASection';

export default function HomePage() {
  // FORCE REDEPLOY - Phoenix Aube + Trajectory Builder IA - Version 2025
  return (
    <main className="flex min-h-screen flex-col items-center justify-between">
      <HeroSection />
      <EcosystemSection />
      <CTASection />
    </main>
  );
}

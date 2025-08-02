import HonestHeroSection from '@/components/sections/HonestHeroSection';
import WhyNowSection from '@/components/sections/WhyNowSection';
import EcosystemSection from '@/components/sections/EcosystemSection';
import HonestMetricsSection from '@/components/sections/HonestMetricsSection';
import AuthenticTestimonialsSection from '@/components/sections/AuthenticTestimonialsSection';

export default function Home() {
  return (
    <div className="flex flex-col">
      <HonestHeroSection />
      <WhyNowSection />
      <EcosystemSection />
      <HonestMetricsSection />
      <AuthenticTestimonialsSection />
    </div>
  );
}

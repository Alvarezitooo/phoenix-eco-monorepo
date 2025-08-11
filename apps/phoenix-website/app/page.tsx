// apps/phoenix-website/app/page.tsx
'use client';

import DojoMental from '../components/DojoMental/DojoMental';
import { RenderHtml } from '../components/RenderHtml';

export default function HomePage() {
  // Remplacez 'some_user_id' par un ID utilisateur réel ou simulé
  const userId = 'user_12345';
  const bannerHtml = process.env.NEXT_PUBLIC_USER_BANNER_HTML;
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      {bannerHtml ? <RenderHtml html={bannerHtml} /> : null}
      <DojoMental userId={userId} />
    </main>
  );
}

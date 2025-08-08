// apps/phoenix-website/app/page.tsx
'use client';

import DojoMental from '../components/DojoMental/DojoMental';

export default function HomePage() {
  // Remplacez 'some_user_id' par un ID utilisateur réel ou simulé
  const userId = "user_12345"; 
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <DojoMental userId={userId} />
    </main>
  );
}
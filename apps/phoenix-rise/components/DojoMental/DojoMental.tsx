import React, { useState, useEffect, useRef } from 'react';
// ✅ CORRECTION ARCHITECTURE: Import depuis packages partagés
import { ZazenTimer, KaizenGrid } from '../../../../packages/phoenix-shared-ui/components';
// ✅ CORRECTION ARCHITECTURE: Logique réseau externalisée
import { useDojoApi } from './hooks/useDojoApi';

interface DojoMentalProps {
  userId: string;
}

export default function DojoMental({ userId }: DojoMentalProps) {
  const [currentDialogue, setCurrentDialogue] = useState("");
  const [kaizenInput, setKaizenInput] = useState("");
  const kaizenGridRef = useRef<{ refreshKaizenHistory: () => void }>(null);
  
  // ✅ CORRECTION ARCHITECTURE: Logique API externalisée
  const { createKaizen, createZazenSession, isLoading, error } = useDojoApi();

  useEffect(() => {
    // Initial Iris dialogue based on Annexe 2
    setCurrentDialogue("Bienvenue dans le Dojo. Tu n’es pas ici pour tout résoudre, juste pour faire un pas. Lequel ?");
  }, []);

  // ✅ CORRECTION ARCHITECTURE: Logique métier simplifiée
  const handleKaizenSubmit = async () => {
    if (!kaizenInput.trim() || isLoading) return;

    const kaizenData = {
      user_id: userId,
      action: kaizenInput.trim(),
      date: new Date().toISOString().split('T')[0],
      completed: false,
    };

    const result = await createKaizen(kaizenData);
    
    if (result.success) {
      setKaizenInput("");
      setCurrentDialogue("Un excellent choix. Ce Kaizen est enregistré. Que souhaites-tu faire ensuite ?");
      if (kaizenGridRef.current) {
        kaizenGridRef.current.refreshKaizenHistory();
      }
    } else {
      setCurrentDialogue(`Désolé, une erreur est survenue: ${result.error}`);
    }
  };

  // ✅ CORRECTION ARCHITECTURE: Logique métier simplifiée
  const handleZazenStart = async () => {
    if (isLoading) return;

    const sessionData = {
      user_id: userId,
      timestamp: new Date().toISOString(),
      duration: 120, // 2 minutes
      triggered_by: "user_request",
    };

    const result = await createZazenSession(sessionData);
    
    if (result.success) {
      setCurrentDialogue("Très bien. Commençons ce Zazen de 2 minutes. Concentre-toi sur ta respiration.");
      // Trigger ZazenTimer start here
    } else {
      setCurrentDialogue(`Désolé, une erreur est survenue: ${result.error}`);
    }
  };

  return (
    <div className="dojo-mental-container p-8 bg-gray-50 min-h-screen flex flex-col items-center">
      <h1 className="text-4xl font-bold text-gray-800 mb-8">Le Dojo Mental</h1>

      <div className="dojo-dialogue-box bg-white p-6 rounded-lg shadow-md max-w-xl text-center mb-8">
        <p className="text-lg text-gray-700">{currentDialogue}</p>
      </div>

      <div className="dojo-interaction-area flex flex-col items-center space-y-4 mb-12">
        <input
          type="text"
          className="w-full max-w-md p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          placeholder="Ton Kaizen du jour..."
          value={kaizenInput}
          onChange={(e) => setKaizenInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleKaizenSubmit();
            }
          }}
        />
        <button
          className={`px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={handleKaizenSubmit}
          disabled={isLoading}
        >
          {isLoading ? 'Enregistrement...' : 'Enregistrer mon Kaizen'}
        </button>
        <button
          className={`px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={handleZazenStart}
          disabled={isLoading}
        >
          {isLoading ? 'Démarrage...' : 'Commencer un Zazen de 2 minutes'}
        </button>
      </div>

      <div className="dojo-visual-components grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl">
        <div className="zazen-timer-section bg-white p-6 rounded-lg shadow-md flex flex-col items-center justify-center">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Zazen Timer</h2>
          <ZazenTimer />
        </div>
        <div className="kaizen-grid-section bg-white p-6 rounded-lg shadow-md flex flex-col items-center justify-center">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Kaizen Grid</h2>
          <KaizenGrid userId={userId} ref={kaizenGridRef} />
        </div>
      </div>
    </div>
  );
}

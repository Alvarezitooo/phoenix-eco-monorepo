import React, { useState, useEffect } from 'react';
import ZazenTimer from '../../../../apps/phoenix-website/components/ZazenTimer/ZazenTimer';
import KaizenGrid from '../../../../apps/phoenix-website/components/KaizenGrid/KaizenGrid';

const API_BASE_URL = process.env.NEXT_PUBLIC_DOJO_API_URL || "http://127.0.0.1:8000";

interface DojoMentalProps {
  userId: string;
}

export default function DojoMental({ userId }: DojoMentalProps) {
  const [currentDialogue, setCurrentDialogue] = useState("");
  const [kaizenInput, setKaizenInput] = useState("");

  useEffect(() => {
    // Initial Iris dialogue based on Annexe 2
    setCurrentDialogue("Bienvenue dans le Dojo. Tu n’es pas ici pour tout résoudre, juste pour faire un pas. Lequel ?");
  }, []);

  const handleKaizenSubmit = async () => {
    if (kaizenInput.trim()) {
      const newKaizen = {
        user_id: userId,
        action: kaizenInput.trim(),
        date: new Date().toISOString().split('T')[0],
        completed: false,
      };
      try {
        const response = await fetch(`${API_BASE_URL}/kaizen`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newKaizen),
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Kaizen created:", data);
        setKaizenInput("");
        setCurrentDialogue("Un excellent choix. Ce Kaizen est enregistré. Que souhaites-tu faire ensuite ?");
        // In a real app, you'd trigger a refresh of KaizenGrid data here
      } catch (error) {
        console.error("Error creating Kaizen:", error);
        setCurrentDialogue("Désolé, une erreur est survenue lors de l'enregistrement de votre Kaizen.");
      }
    }
  };

  const handleZazenStart = async () => {
    const sessionData = {
      user_id: userId,
      timestamp: new Date().toISOString(),
      duration: 120, // 2 minutes
      triggered_by: "user_request",
    };
    try {
      const response = await fetch(`${API_BASE_URL}/zazen-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionData),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log("Zazen session created:", data);
      setCurrentDialogue("Très bien. Commençons ce Zazen de 2 minutes. Concentre-toi sur ta respiration.");
      // Trigger ZazenTimer start here
    } catch (error) {
      console.error("Error creating Zazen session:", error);
      setCurrentDialogue("Désolé, une erreur est survenue lors du démarrage de votre Zazen.");
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
          className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
          onClick={handleKaizenSubmit}
        >
          Enregistrer mon Kaizen
        </button>
        <button
          className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
          onClick={handleZazenStart}
        >
          Commencer un Zazen de 2 minutes
        </button>
      </div>

      <div className="dojo-visual-components grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl">
        <div className="zazen-timer-section bg-white p-6 rounded-lg shadow-md flex flex-col items-center justify-center">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Zazen Timer</h2>
          <ZazenTimer />
        </div>
        <div className="kaizen-grid-section bg-white p-6 rounded-lg shadow-md flex flex-col items-center justify-center">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Kaizen Grid</h2>
          <KaizenGrid userId={userId} />
        </div>
      </div>
    </div>
  );
}
'use client';
import React, { useEffect, useMemo, useState } from 'react';

type Kaizen = { id?: number; user_id: string; action: string; date: string; completed?: boolean };

const USER_ID = 'test_user_123';

async function safeFetch(input: RequestInfo, init?: RequestInit) {
  try {
    const res = await fetch(input, init);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    return null;
  }
}

function useDojoApi() {
  const baseUrl = process.env.NEXT_PUBLIC_DOJO_API_URL || 'http://localhost:8000';

  const api = useMemo(
    () => ({
      async listKaizen(): Promise<Kaizen[]> {
        const data = await safeFetch(`${baseUrl}/kaizen/${USER_ID}`);
        if (data) return data as Kaizen[];
        const local = localStorage.getItem('dojo_kaizen');
        return local ? (JSON.parse(local) as Kaizen[]) : [];
      },
      async createKaizen(action: string, dateISO: string) {
        const payload: Kaizen = { user_id: USER_ID, action, date: dateISO, completed: false };
        const data = await safeFetch(`${baseUrl}/kaizen`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (data) return data as Kaizen;
        const list = await this.listKaizen();
        const offline: Kaizen = { ...payload, id: Date.now() };
        localStorage.setItem('dojo_kaizen', JSON.stringify([offline, ...list]));
        return offline;
      },
      async completeKaizen(id: number) {
        const data = await safeFetch(`${baseUrl}/kaizen/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ completed: true }),
        });
        if (data) return data as Kaizen;
        const list = await this.listKaizen();
        const next = list.map((k) => (k.id === id ? { ...k, completed: true } : k));
        localStorage.setItem('dojo_kaizen', JSON.stringify(next));
        return next.find((k) => k.id === id);
      },
    }),
    [baseUrl],
  );

  return api;
}

export default function DojoPage() {
  const api = useDojoApi();
  const [kaizen, setKaizen] = useState<Kaizen[]>([]);
  const [action, setAction] = useState('');

  useEffect(() => {
    api.listKaizen().then(setKaizen);
  }, [api]);

  async function addKaizen() {
    if (!action.trim()) return;
    const dateISO = new Date().toISOString().slice(0, 10);
    const created = await api.createKaizen(action.trim(), dateISO);
    setKaizen((prev) => [created, ...prev]);
    setAction('');
  }

  async function toggleComplete(k: Kaizen) {
    if (!k.id) return;
    const updated = await api.completeKaizen(k.id);
    setKaizen((prev) => prev.map((x) => (x.id === updated?.id ? (updated as Kaizen) : x)));
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-semibold mb-6">Dojo Mental</h1>
      <div className="flex gap-2 mb-6">
        <input
          className="flex-1 border rounded px-3 py-2"
          placeholder="Micro-action Kaizen (≤ 2 min)"
          value={action}
          onChange={(e) => setAction(e.target.value)}
        />
        <button className="bg-black text-white px-4 py-2 rounded" onClick={addKaizen}>
          Ajouter
        </button>
      </div>
      <ul className="space-y-2">
        {kaizen.map((k) => (
          <li
            key={k.id ?? `${k.action}-${k.date}`}
            className="border rounded p-3 flex items-center justify-between"
          >
            <div>
              <div className="font-medium">{k.action}</div>
              <div className="text-sm text-gray-500">{k.date}</div>
            </div>
            <button
              className={`px-3 py-1 rounded text-sm ${k.completed ? 'bg-green-600 text-white' : 'bg-gray-200'}`}
              onClick={() => toggleComplete(k)}
              disabled={!k.id}
              title={!k.id ? 'Terminer après synchro' : 'Marquer comme fait'}
            >
              {k.completed ? 'Fait' : 'Terminer'}
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}

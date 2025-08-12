import { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_DOJO_API_URL || 'http://127.0.0.1:8001';

interface KaizenData {
  id?: number;
  user_id: string;
  action: string;
  date: string;
  completed: boolean;
}

interface UseKaizenHistoryResult {
  data: KaizenData[];
  loading: boolean;
  error: string | null;
  toggleKaizenStatus: (date: string) => Promise<void>;
  refreshKaizenHistory: () => void;
}

export function useKaizenHistory(userId: string): UseKaizenHistoryResult {
  const [data, setData] = useState<KaizenData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchKaizenHistory = useCallback(async () => {
    if (!userId) return;
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/kaizen/${userId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('phoenix_auth_token')}`
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result: KaizenData[] = await response.json();
      setData(result);
    } catch (err: any) {
      setError(`Failed to fetch Kaizen history: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchKaizenHistory();
  }, [fetchKaizenHistory]);

  const toggleKaizenStatus = useCallback(
    async (dateToToggle: string) => {
      const itemToUpdate = data.find((item) => item.date === dateToToggle);
      if (!itemToUpdate || itemToUpdate.id === undefined) {
        console.error('Kaizen item not found or has no ID:', dateToToggle);
        return;
      }

      const originalData = [...data];

      setData((prevData) =>
        prevData.map((item) =>
          item.date === dateToToggle ? { ...item, completed: !item.completed } : item,
        ),
      );

      try {
        const updatedStatus = !itemToUpdate.completed;
        const response = await fetch(`${API_BASE_URL}/kaizen/${itemToUpdate.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('phoenix_auth_token')}`
          },
          body: JSON.stringify({ completed: updatedStatus }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        await response.json();
      } catch (err: any) {
        setError(`Failed to update Kaizen status: ${err.message}`);
        setData(originalData);
      }
    },
    [data, userId],
  );

  return { data, loading, error, toggleKaizenStatus, refreshKaizenHistory: fetchKaizenHistory };
}
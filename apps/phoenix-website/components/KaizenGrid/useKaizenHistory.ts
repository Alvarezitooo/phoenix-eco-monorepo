import { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_DOJO_API_URL || 'http://127.0.0.1:8000';

interface KaizenData {
  id?: number; // Optional for creation, present for fetched data
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
      const response = await fetch(`${API_BASE_URL}/kaizen/${userId}`);
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

      const originalData = [...data]; // Save original data for rollback

      // Optimistic UI update
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
          },
          body: JSON.stringify({ completed: updatedStatus }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        // No need to parse response if we trust optimistic update, but good for logging
        await response.json();
      } catch (err: any) {
        setError(`Failed to update Kaizen status: ${err.message}`);
        setData(originalData); // Rollback on error
      }
    },
    [data, userId],
  ); // userId added to dependencies

  return { data, loading, error, toggleKaizenStatus, refreshKaizenHistory: fetchKaizenHistory };
}

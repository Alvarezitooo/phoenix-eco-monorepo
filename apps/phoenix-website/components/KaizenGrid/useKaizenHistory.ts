import { useState, useEffect } from 'react';

interface KaizenData {
  date: string;
  isDone: boolean;
}

interface UseKaizenHistoryResult {
  data: KaizenData[];
  loading: boolean;
  error: string | null;
  toggleKaizenStatus: (date: string) => Promise<void>;
}

// Simulate fetching 365 days of data
const simulateFetchKaizenHistory = (): Promise<KaizenData[]> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const history: KaizenData[] = [];
      const today = new Date();
      for (let i = 0; i < 365; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        history.push({
          date: date.toISOString().split('T')[0], // YYYY-MM-DD
          isDone: Math.random() > 0.5, // Randomly true/false
        });
      }
      resolve(history.reverse()); // Oldest first
    }, 1000); // Simulate network delay
  });
};

// Simulate backend update
const simulateUpdateKaizenStatus = (date: string, isDone: boolean): Promise<void> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      console.log(`Backend updated: ${date} to ${isDone}`);
      resolve();
    }, 300); // Simulate network delay
  });
};

export function useKaizenHistory(): UseKaizenHistoryResult {
  const [data, setData] = useState<KaizenData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await simulateFetchKaizenHistory();
        setData(result);
      } catch (err) {
        setError('Failed to fetch Kaizen history.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const toggleKaizenStatus = async (dateToToggle: string) => {
    const originalData = [...data]; // Save original data for rollback

    // Optimistic UI update
    setData((prevData) =>
      prevData.map((item) =>
        item.date === dateToToggle ? { ...item, isDone: !item.isDone } : item,
      ),
    );

    try {
      const itemToUpdate = data.find((item) => item.date === dateToToggle);
      if (itemToUpdate) {
        await simulateUpdateKaizenStatus(dateToToggle, !itemToUpdate.isDone);
      }
    } catch (err) {
      setError('Failed to update Kaizen status.');
      setData(originalData); // Rollback on error
    }
  };

  return { data, loading, error, toggleKaizenStatus };
}

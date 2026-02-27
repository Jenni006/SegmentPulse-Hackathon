import { useState, useEffect, useCallback, useRef } from 'react';

export function usePolling<T>(
  fetchFn: () => Promise<T>,
  interval: number,
  enabled: boolean = true
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const isFetching = useRef(false);  // ← prevents overlap

  const fetchData = useCallback(async () => {
    if (isFetching.current) return;  // ← skip if already running
    isFetching.current = true;
    try {
      const result = await fetchFn();
      setData(result);
      setError(null);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setLoading(false);
    } finally {
      isFetching.current = false;  // ← always release
    }
  }, [fetchFn]);

  useEffect(() => {
    if (!enabled) return;
    fetchData();
    const intervalId = setInterval(fetchData, interval);
    return () => clearInterval(intervalId);
  }, [fetchData, interval, enabled]);

  return { data, loading, error, refetch: fetchData };
}

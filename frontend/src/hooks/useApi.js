import { useCallback, useEffect, useRef, useState } from "react";

export function useApi(loader) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const hasLoaded = useRef(false);

  const refresh = useCallback(async ({ silent = false } = {}) => {
    const isInitialLoad = !hasLoaded.current;

    try {
      setError(null);
      if (isInitialLoad && !silent) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }
      const nextData = await loader();
      setData(nextData);
      hasLoaded.current = true;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [loader]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, error, loading, refreshing, refresh, setData };
}

import { createContext, useCallback, useContext, useMemo, useState } from 'react';

const DataRefreshContext = createContext(null);

export function DataRefreshProvider({ children }) {
  const [tick, setTick] = useState(0);

  const refreshAll = useCallback(() => {
    setTick((t) => t + 1);
  }, []);

  const value = useMemo(() => ({ tick, refreshAll }), [tick, refreshAll]);

  return <DataRefreshContext.Provider value={value}>{children}</DataRefreshContext.Provider>;
}

export function useDataRefresh() {
  const ctx = useContext(DataRefreshContext);
  if (!ctx) {
    return { tick: 0, refreshAll: () => {} };
  }
  return ctx;
}

import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchCatalog } from "./lib/api";
import { matchesFilter } from "./lib/sensor";
import { HeaderBar } from "./components/HeaderBar";
import { MissionPlayer } from "./components/MissionPlayer";
import { SequenceExplorer } from "./components/SequenceExplorer";
import { TelemetryPanel } from "./components/TelemetryPanel";
import type { CatalogSequence, SensorFilter } from "./types";

export default function App() {
  const [filter, setFilter] = useState<SensorFilter>("VIS");
  const [catalog, setCatalog] = useState<CatalogSequence[]>([]);
  const [active, setActive] = useState<CatalogSequence | null>(null);
  const [frameIndex, setFrameIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const items = await fetchCatalog();
        if (cancelled) return;
        setCatalog(items);
      } catch {
        if (!cancelled) {
          setError("Cannot connect to the API. Start the backend on port 8000.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = useMemo(
    () => catalog.filter((s) => matchesFilter(s.sensor, filter)),
    [catalog, filter],
  );

  useEffect(() => {
    if (filtered.length === 0) {
      setActive(null);
      return;
    }
    if (!active || !filtered.some((s) => s.id === active.id)) {
      setActive(filtered[0]);
      setFrameIndex(0);
    }
  }, [active, filtered]);

  const handleSelect = useCallback((seq: CatalogSequence) => {
    setActive(seq);
    setFrameIndex(0);
    setError(null);
  }, []);

  const handleFilterChange = useCallback((f: SensorFilter) => {
    setFilter(f);
    setFrameIndex(0);
  }, []);

  return (
    <div className="flex min-h-screen flex-col">
      <HeaderBar filter={filter} onFilterChange={handleFilterChange} />

      {error && (
        <div className="border-b border-red-200 bg-red-50 px-6 py-2 text-sm text-red-800">{error}</div>
      )}

      {loading ? (
        <div className="flex flex-1 items-center justify-center text-sm text-slate-600">Loading…</div>
      ) : (
        <main className="mx-auto grid w-full max-w-[1600px] min-h-0 flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-[240px_1fr_240px]">
          <SequenceExplorer
            sequences={filtered}
            activeId={active?.id ?? null}
            sensorFilter={filter}
            onSelect={handleSelect}
          />
          <MissionPlayer
            sequence={active}
            frameIndex={frameIndex}
            onFrameIndexChange={setFrameIndex}
          />
          <TelemetryPanel sequence={active} frameIndex={frameIndex} />
        </main>
      )}
    </div>
  );
}

import type { CatalogSequence, SensorFilter } from "../types";

interface SequenceExplorerProps {
  sequences: CatalogSequence[];
  activeId: string | null;
  sensorFilter: SensorFilter;
  onSelect: (seq: CatalogSequence) => void;
}

const FILTER_LABEL: Record<SensorFilter, string> = {
  VIS: "VIS",
  NIR: "NIR",
  REDNIR: "Red-NIR",
};

export function SequenceExplorer({
  sequences,
  activeId,
  sensorFilter,
  onSelect,
}: SequenceExplorerProps) {
  return (
    <aside className="panel flex h-full flex-col overflow-hidden">
      <h2 className="panel-heading">{FILTER_LABEL[sensorFilter]} sequences</h2>
      <div className="flex-1 space-y-1 overflow-y-auto p-2">
        {sequences.length === 0 && (
          <p className="px-3 py-6 text-sm text-slate-600">No sequences for this filter.</p>
        )}
        {sequences.map((seq) => {
          const active = seq.id === activeId;
          return (
            <button
              key={seq.id}
              type="button"
              onClick={() => onSelect(seq)}
              className={`w-full rounded-md border px-3 py-3 text-left transition ${
                active
                  ? "border-blue-200 bg-slate-50 ring-1 ring-blue-100"
                  : "border-transparent hover:border-slate-200 hover:bg-slate-50"
              }`}
            >
              <div>
                <p className="text-sm font-medium text-slate-900">{seq.display_name}</p>
                <p className="mt-0.5 text-xs text-slate-600">{seq.seq_name}</p>
              </div>
              <p className="mt-2 text-xs text-slate-500">{seq.frame_count} frames</p>
            </button>
          );
        })}
      </div>
    </aside>
  );
}

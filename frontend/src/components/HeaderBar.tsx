import type { SensorFilter } from "../types";

const SENSORS: { id: SensorFilter; label: string }[] = [
  { id: "VIS", label: "VIS" },
  { id: "NIR", label: "NIR" },
  { id: "REDNIR", label: "Red-NIR" },
];

interface HeaderBarProps {
  filter: SensorFilter;
  onFilterChange: (f: SensorFilter) => void;
}

export function HeaderBar({ filter, onFilterChange }: HeaderBarProps) {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-[1600px] px-6 pt-5">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Affine</p>
        <h1 className="mt-1 text-2xl font-semibold text-slate-900">Hyperspectral Video Tracking</h1>
        <p className="mt-1 text-sm text-slate-600">Review sequences by sensor band</p>
      </div>

      <nav
        className="mx-auto mt-5 flex max-w-[1600px] gap-0 border-t border-slate-200 px-6"
        aria-label="Sensor bands"
      >
        {SENSORS.map(({ id, label }) => {
          const active = filter === id;
          return (
            <button
              key={id}
              type="button"
              onClick={() => onFilterChange(id)}
              className={`-mb-px border-b-2 px-4 py-3 text-sm font-medium transition ${
                active
                  ? "border-blue-800 text-blue-800"
                  : "border-transparent text-slate-600 hover:border-slate-300 hover:text-slate-900"
              }`}
            >
              {label}
            </button>
          );
        })}
      </nav>
    </header>
  );
}

import type { CatalogSequence } from "../types";
import { SensorBadge } from "./SensorBadge";

interface TelemetryPanelProps {
  sequence: CatalogSequence | null;
  frameIndex: number;
}

export function TelemetryPanel({ sequence, frameIndex }: TelemetryPanelProps) {
  const total = sequence?.frame_count ?? 0;

  return (
    <aside className="panel flex h-full flex-col overflow-hidden">
      <h2 className="panel-heading">Playback</h2>

      <div className="space-y-4 p-4 text-sm">
        {sequence ? (
          <>
            <div>
              <p className="text-slate-600">Sequence</p>
              <p className="mt-0.5 font-medium text-slate-900">{sequence.display_name}</p>
            </div>
            <div>
              <p className="text-slate-600">Sensor</p>
              <div className="mt-1">
                <SensorBadge sensor={sequence.sensor} />
              </div>
            </div>
            <div>
              <p className="text-slate-600">Frame</p>
              <p className="mt-0.5 font-medium tabular-nums text-slate-900">
                {total > 0 ? frameIndex + 1 : 0} / {total}
              </p>
            </div>
            <div>
              <p className="text-slate-600">Resolution</p>
              <p className="mt-0.5 tabular-nums text-slate-900">
                {sequence.video_width} × {sequence.video_height}
              </p>
            </div>
            <div>
              <p className="text-slate-600">Frame rate</p>
              <p className="mt-0.5 tabular-nums text-slate-900">{sequence.fps.toFixed(1)} fps</p>
            </div>
          </>
        ) : (
          <p className="text-slate-600">Select a sequence to view details.</p>
        )}
      </div>
    </aside>
  );
}

import type { SensorBand } from "../types";
import { sensorBadgeClass, sensorBadgeLabel } from "../lib/sensor";

interface SensorBadgeProps {
  sensor: SensorBand;
  className?: string;
}

export function SensorBadge({ sensor, className = "" }: SensorBadgeProps) {
  return (
    <span
      className={`inline-flex rounded border px-2 py-0.5 text-xs font-medium ${sensorBadgeClass(sensor)} ${className}`}
    >
      {sensorBadgeLabel(sensor)}
    </span>
  );
}

import type { SensorBand, SensorFilter } from "../types";

export function sensorBadgeLabel(sensor: SensorBand): string {
  switch (sensor) {
    case "VIS":
      return "VIS";
    case "rednir":
      return "Red-NIR";
    case "nir":
      return "NIR";
  }
}

export function sensorBadgeClass(_sensor: SensorBand): string {
  return "border-slate-200 bg-slate-100 text-slate-600";
}

export function filterToSensor(filter: SensorFilter): SensorBand {
  switch (filter) {
    case "VIS":
      return "VIS";
    case "REDNIR":
      return "rednir";
    case "NIR":
      return "nir";
  }
}

export function matchesFilter(sensor: SensorBand, filter: SensorFilter): boolean {
  return sensor === filterToSensor(filter);
}

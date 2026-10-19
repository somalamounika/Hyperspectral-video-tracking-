export type SensorBand = "VIS" | "rednir" | "nir";

export type SensorFilter = "VIS" | "REDNIR" | "NIR";

export interface CatalogSequence {
  id: string;
  sensor: SensorBand;
  sensor_slug: string;
  seq_name: string;
  display_name: string;
  frame_count: number;
  video_width: number;
  video_height: number;
  fps: number;
  stream_url: string;
}

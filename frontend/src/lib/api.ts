import type { CatalogSequence } from "../types";

export async function fetchCatalog(): Promise<CatalogSequence[]> {
  const res = await fetch("/api/catalog");
  if (!res.ok) throw new Error("Failed to load catalog");
  const data = (await res.json()) as { sequences: CatalogSequence[] };
  return data.sequences.map((seq) => ({
    ...seq,
    frame_count: seq.frame_count ?? 0,
    video_width: seq.video_width ?? 0,
    video_height: seq.video_height ?? 0,
    fps: seq.fps ?? 15,
  }));
}

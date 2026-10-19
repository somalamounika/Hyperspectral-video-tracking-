import { ChevronLeft, ChevronRight, Pause, Play } from "lucide-react";
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import type { CatalogSequence } from "../types";
interface MissionPlayerProps {
  sequence: CatalogSequence | null;
  frameIndex: number;
  onFrameIndexChange: (index: number) => void;
}

export function MissionPlayer({
  sequence,
  frameIndex,
  onFrameIndexChange,
}: MissionPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const [playing, setPlaying] = useState(false);
  const [videoError, setVideoError] = useState<string | null>(null);

  const frameCount = sequence?.frame_count ?? 0;
  const fps = sequence?.fps && sequence.fps > 0 ? sequence.fps : 15;

  const syncStageSize = useCallback(() => {
    const video = videoRef.current;
    const container = containerRef.current;
    const stage = stageRef.current;
    if (!video || !container || !stage) return;

    const rect = container.getBoundingClientRect();
    const vw = video.videoWidth || 16;
    const vh = video.videoHeight || 9;
    const aspect = vw / vh;
    let w = rect.width;
    let h = w / aspect;
    if (h > rect.height) {
      h = rect.height;
      w = h * aspect;
    }
    stage.style.width = `${Math.floor(w)}px`;
    stage.style.height = `${Math.floor(h)}px`;
  }, []);

  const getFrameFromTime = useCallback(
    (time: number, duration: number) => {
      if (frameCount <= 0) return 0;
      let idx = Math.floor(time * fps + 1e-4);
      if (duration > 0 && frameCount > 1) {
        const byDuration = Math.round((time / duration) * (frameCount - 1));
        if (Math.abs(byDuration - idx) > 2) idx = byDuration;
      }
      return Math.max(0, Math.min(idx, frameCount - 1));
    },
    [frameCount, fps],
  );

  const syncFrameFromVideo = useCallback(() => {
    const video = videoRef.current;
    if (!video || !sequence) return;
    const idx =
      video.duration && frameCount > 0
        ? getFrameFromTime(video.currentTime, video.duration)
        : frameIndex;
    onFrameIndexChange(idx);
  }, [frameCount, frameIndex, getFrameFromTime, onFrameIndexChange, sequence]);

  const seekToFrame = useCallback(
    (index: number) => {
      const video = videoRef.current;
      if (!video || !sequence) return;
      const clamped = Math.max(0, Math.min(index, Math.max(frameCount - 1, 0)));
      if (fps > 0) video.currentTime = clamped / fps;
      else if (video.duration && frameCount > 1) {
        video.currentTime = (clamped / (frameCount - 1)) * video.duration;
      }
      onFrameIndexChange(clamped);
    },
    [frameCount, fps, onFrameIndexChange, sequence],
  );

  useLayoutEffect(() => {
    syncStageSize();
    const ro = new ResizeObserver(() => syncStageSize());
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, [syncStageSize, sequence?.id]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const onLoaded = () => {
      syncStageSize();
      seekToFrame(0);
    };
    const onPlay = () => setPlaying(true);
    const onPause = () => setPlaying(false);

    video.addEventListener("loadedmetadata", onLoaded);
    video.addEventListener("timeupdate", syncFrameFromVideo);
    video.addEventListener("seeked", syncFrameFromVideo);
    video.addEventListener("play", onPlay);
    video.addEventListener("pause", onPause);

    return () => {
      video.removeEventListener("loadedmetadata", onLoaded);
      video.removeEventListener("timeupdate", syncFrameFromVideo);
      video.removeEventListener("seeked", syncFrameFromVideo);
      video.removeEventListener("play", onPlay);
      video.removeEventListener("pause", onPause);
    };
  }, [seekToFrame, sequence?.stream_url, syncStageSize, syncFrameFromVideo]);

  useEffect(() => {
    if (!sequence) return;
    const video = videoRef.current;
    if (!video) return;
    setVideoError(null);
    video.src = sequence.stream_url;
    video.load();
    setPlaying(false);
    seekToFrame(0);
  }, [sequence, seekToFrame]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement | null)?.tagName ?? "";
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      if (e.code === "Space") {
        e.preventDefault();
        const v = videoRef.current;
        if (!v || !sequence) return;
        if (v.paused) void v.play();
        else v.pause();
      }
      if (e.key === "<" || e.key === ",") {
        e.preventDefault();
        seekToFrame(frameIndex - 1);
      }
      if (e.key === ">" || e.key === ".") {
        e.preventDefault();
        seekToFrame(frameIndex + 1);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [frameIndex, seekToFrame, sequence]);

  const togglePlay = () => {
    const v = videoRef.current;
    if (!v) return;
    if (v.paused) void v.play();
    else v.pause();
  };

  return (
    <section className="panel flex min-h-0 flex-1 flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-sm font-semibold text-slate-900">Video</h2>
        {sequence && <span className="text-xs text-slate-600">{sequence.display_name}</span>}
      </div>

      <div ref={containerRef} className="relative flex flex-1 items-center justify-center bg-neutral-900 p-4">
        {!sequence && <p className="text-sm text-neutral-400">Select a sequence.</p>}
        {sequence && (
          <div ref={stageRef} className="relative overflow-hidden bg-black">
            <video
              ref={videoRef}
              className="h-full w-full object-contain"
              playsInline
              preload="auto"
              onError={() =>
                setVideoError(
                  "This video format cannot play in the browser. Restart the backend or re-run clean_video_overlays.py.",
                )
              }
            />
            {videoError && (
              <p className="absolute inset-x-2 bottom-2 rounded bg-red-950/90 px-2 py-1 text-center text-xs text-red-100">
                {videoError}
              </p>
            )}
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-center justify-center gap-2 border-t border-slate-200 px-4 py-3">
        <button type="button" disabled={!sequence} onClick={() => seekToFrame(frameIndex - 1)} className="btn-secondary">
          <ChevronLeft className="h-4 w-4" />
          Previous
        </button>
        <button type="button" disabled={!sequence} onClick={togglePlay} className="btn-primary">
          {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          {playing ? "Pause" : "Play"}
        </button>
        <button type="button" disabled={!sequence} onClick={() => seekToFrame(frameIndex + 1)} className="btn-secondary">
          Next
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </section>
  );
}

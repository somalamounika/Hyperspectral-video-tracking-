from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import SEQUENCES, resolve_sequence, video_path_for
from .streaming import stream_file
from .video_meta import probe_video

app = FastAPI(
    title="Hyperspectral Video Tracking API",
    version="1.0.0",
    description="Video catalog and byte-range streaming for HSI sequences.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "Accept-Ranges", "Content-Length"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/catalog")
def catalog():
    items = []
    for key, meta in SEQUENCES.items():
        sensor_slug = meta["sensor_slug"]
        seq_name = meta["seq_name"]
        video_path = video_path_for(meta)
        probe = probe_video(str(video_path))
        frames = probe["video_frame_count"] or 0
        items.append(
            {
                "id": key,
                "sensor": meta["sensor"],
                "sensor_slug": sensor_slug,
                "seq_name": seq_name,
                "display_name": meta["display_name"],
                "frame_count": frames,
                "video_width": probe["width"],
                "video_height": probe["height"],
                "fps": probe["fps"],
                "stream_url": f"/api/stream/{sensor_slug}/{seq_name}",
            }
        )
    return {"sequences": items}


@app.get("/api/stream/{sensor}/{seq_name}")
def get_stream(sensor: str, seq_name: str, request: Request):
    resolved = resolve_sequence(sensor, seq_name)
    if resolved is None:
        raise HTTPException(status_code=404, detail="Sequence not found")

    _key, meta = resolved
    path = video_path_for(meta)
    range_header = request.headers.get("range")
    return stream_file(path, range_header)

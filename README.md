# Hyperspectral Video Tracking

Video review dashboard for VIS, NIR, and Red-NIR sequences. Bounding boxes are embedded in the source videos; no CSV track files are used.

## Prerequisites

- Python 3.10+
- Node.js 18+

## Video files

Place MP4s under `backend/data/` (see `backend/app/config.py` for paths). Named `video.mp4` or any single `.mp4` in each sequence folder.

## Run

**Backend** (port 8000):

```powershell
cd backend
.\run.ps1
```

**Frontend** (port 5173):

```powershell
cd frontend
.\run.ps1
```

Open **http://127.0.0.1:5173**

### Why two (or three) MP4 files?

| File | Purpose |
|------|---------|
| **Original** (e.g. `car11.mp4`) | Your uploaded source |
| **`*_clean.mp4`** | Optional: legend removed via inpainting (only used if H.264) |
| **`*_web.mp4`** | Auto-created **H.264** copy when the original uses **mp4v** (common for Call 11) so the browser can play it |

The API picks the first **browser-playable** file: `_clean` → `_web` → original.

```powershell
cd backend
.\.venv\Scripts\python scripts/ensure_web_videos.py
.\.venv\Scripts\python scripts/clean_video_overlays.py --force
```

You may delete old `*_clean.mp4` files that were made before H.264 encoding; re-run `clean_video_overlays.py --force` to regenerate.

## UI

1. **Affine** — organization line  
2. **Hyperspectral Video Tracking** — title  
3. **VIS / NIR / Red-NIR** — sensor tabs; sequences list updates per tab  
4. **Video** — full-frame playback (any OpenCV text/boxes are part of the MP4)  
5. **Playback** — frame counter and metadata (no CSV telemetry)

## API

- `GET /api/catalog` — sequences and stream URLs  
- `GET /api/stream/{sensor}/{seq_name}` — MP4 with byte-range support  

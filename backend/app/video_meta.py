from __future__ import annotations

from functools import lru_cache
from pathlib import Path

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


@lru_cache(maxsize=32)
def probe_video(path_str: str) -> dict:
    path = Path(path_str)
    if cv2 is None or not path.is_file():
        return {
            "width": 0,
            "height": 0,
            "video_frame_count": 0,
            "fps": 0.0,
        }

    cap = cv2.VideoCapture(str(path))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    cap.release()

    if fps <= 0:
        fps = 15.0

    return {
        "width": width,
        "height": height,
        "video_frame_count": frame_count,
        "fps": fps,
    }

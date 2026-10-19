"""Create browser-safe *_web.mp4 (H.264) for any source that uses mp4v."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import SEQUENCES, _resolve_raw_video, is_browser_playable_mp4, DATA_DIR
from app.video_clean import transcode_for_browser


def main() -> None:
    for key, meta in SEQUENCES.items():
        raw = _resolve_raw_video(DATA_DIR / meta["video_rel"])
        if not raw.is_file():
            print(f"SKIP {key}: missing {raw}")
            continue
        if is_browser_playable_mp4(raw):
            print(f"OK   {key}: {raw.name} already H.264")
            continue
        web = raw.with_name(f"{raw.stem}_web{raw.suffix}")
        print(f"WEB  {key}: {raw.name} -> {web.name}")
        n = transcode_for_browser(str(raw), str(web))
        print(f"     {n} frames")


if __name__ == "__main__":
    main()

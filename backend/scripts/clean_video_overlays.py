"""Write H.264 *_clean.mp4 — labels removed; Call 11 boxes normalized to Pred style."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DATA_DIR, SEQUENCES, _resolve_raw_video
from app.video_clean import clean_video_file

NORMALIZE_BOX_KEYS = {"nir-call11"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Rebuild even if _clean.mp4 exists")
    args = parser.parse_args()

    for key, meta in SEQUENCES.items():
        raw = _resolve_raw_video(DATA_DIR / meta["video_rel"])
        if not raw.is_file():
            print(f"SKIP {key}: missing {raw}")
            continue
        dst = raw.with_name(f"{raw.stem}_clean{raw.suffix}")
        if dst.is_file() and not args.force:
            print(f"OK   {key}: {dst.name} already exists")
            continue
        normalize = key in NORMALIZE_BOX_KEYS
        print(f"Clean {key}: {raw.name} -> {dst.name} (normalize_box={normalize}) ...")
        frames = clean_video_file(str(raw), str(dst), normalize_box=normalize)
        print(f"     wrote {frames} frames")


if __name__ == "__main__":
    main()

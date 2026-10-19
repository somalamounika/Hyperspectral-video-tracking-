from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

SEQUENCES: dict[str, dict] = {
    "vis-domino12": {
        "sensor": "VIS",
        "sensor_slug": "vis",
        "seq_name": "domino12",
        "display_name": "Domino 12",
        "video_rel": Path("VIS") / "domino12" / "vis-domino12.mp4",
    },
    "vis-CD": {
        "sensor": "VIS",
        "sensor_slug": "vis",
        "seq_name": "CD",
        "display_name": "CD Mirror",
        "video_rel": Path("VIS") / "CD_mirror1" / "vis-CD_mirror1.mp4",
    },
    "vis-dog": {
        "sensor": "VIS",
        "sensor_slug": "vis",
        "seq_name": "dog",
        "display_name": "Dog",
        "video_rel": Path("VIS") / "dog" / "dog.mp4",
    },
    "vis-doll1": {
        "sensor": "VIS",
        "sensor_slug": "vis",
        "seq_name": "doll1",
        "display_name": "Doll 1",
        "video_rel": Path("VIS") / "doll1" / "doll1.mp4",
    },
    "rednir-soccer1": {
        "sensor": "rednir",
        "sensor_slug": "rednir",
        "seq_name": "soccer1",
        "display_name": "Soccer 1",
        "video_rel": Path("rednir") / "soccer1" / "rednir-soccer1.mp4",
    },
    "rednir-rccar2": {
        "sensor": "rednir",
        "sensor_slug": "rednir",
        "seq_name": "rccar2",
        "display_name": "RC Car 2",
        "video_rel": Path("rednir") / "rccar2" / "rccar2.mp4",
    },
    "rednir-pills7": {
        "sensor": "rednir",
        "sensor_slug": "rednir",
        "seq_name": "pills7",
        "display_name": "Pills 7",
        "video_rel": Path("rednir") / "pills7" / "pills7.mp4",
    },
    "nir-drone": {
        "sensor": "nir",
        "sensor_slug": "nir",
        "seq_name": "drone",
        "display_name": "Drone Mirror",
        "video_rel": Path("nir") / "drone_mirror" / "nir-drone_mirror.mp4",
    },
    "nir-blackball2": {
        "sensor": "nir",
        "sensor_slug": "nir",
        "seq_name": "blackball2",
        "display_name": "Blackball 2",
        "video_rel": Path("nir") / "blackball2" / "nir-blackball2.mp4",
    },
    "nir-call11": {
        "sensor": "nir",
        "sensor_slug": "nir",
        "seq_name": "call11",
        "display_name": "Car 11",
        "video_rel": Path("nir") / "car11" / "car11.mp4",
    },
}


def resolve_sequence(sensor: str, seq_name: str) -> tuple[str, dict] | None:
    sensor_l = sensor.lower()
    for key, meta in SEQUENCES.items():
        if meta["sensor_slug"] == sensor_l and meta["seq_name"] == seq_name:
            return key, meta
    return None


def _is_derivative(stem: str) -> bool:
    return stem.endswith("_clean") or stem.endswith("_web")


def _resolve_raw_video(configured: Path) -> Path:
    if configured.is_file() and not _is_derivative(configured.stem):
        return configured
    folder = configured.parent
    preferred = folder / "video.mp4"
    if preferred.is_file():
        return preferred
    if not folder.is_dir():
        return configured if configured.is_file() else preferred

    mp4s = sorted(p for p in folder.glob("*.mp4") if not _is_derivative(p.stem))
    if not mp4s:
        return preferred
    return mp4s[0]


def is_browser_playable_mp4(path: Path) -> bool:
    """Chrome/Edge need H.264 (avc1). OpenCV mp4v exports usually fail in <video>."""
    if not path.is_file():
        return False
    data = path.read_bytes()
    if b"avc1" in data or b"hvc1" in data:
        return True
    if b"mp4v" in data:
        return False
    return False


def video_path_for(meta: dict) -> Path:
    configured = DATA_DIR / meta["video_rel"]
    raw = _resolve_raw_video(configured)

    # Prefer source footage (labels/boxes baked in). Only transcode for browser codecs.
    candidates = [
        raw,
        raw.with_name(f"{raw.stem}_web{raw.suffix}"),
    ]
    for path in candidates:
        if path.is_file() and is_browser_playable_mp4(path):
            return path

    web = raw.with_name(f"{raw.stem}_web{raw.suffix}")
    if not web.is_file() or not is_browser_playable_mp4(web):
        from .video_clean import transcode_for_browser

        transcode_for_browser(str(raw), str(web))

    if web.is_file() and is_browser_playable_mp4(web):
        return web

    return raw

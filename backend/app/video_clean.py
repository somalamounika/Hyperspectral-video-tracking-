"""Inpaint on-video HUD text; optional green box redraw to match dataset style."""
from __future__ import annotations

import cv2
import imageio.v3 as iio
import numpy as np

# BGR — matches typical OpenCV "Pred" green on domino-style sequences
PRED_BOX_COLOR = (0, 230, 0)
PRED_BOX_THICKNESS = 2


def corner_hud_mask(h: int, w: int) -> np.ndarray:
    mask = np.zeros((h, w), np.uint8)
    mask[0 : max(1, int(h * 0.09)), 0 : max(1, int(w * 0.30))] = 255
    mask[max(0, int(h * 0.82)) : h, 0 : max(1, int(w * 0.55))] = 255
    return mask


def _green_mask(hsv: np.ndarray) -> np.ndarray:
    return cv2.inRange(hsv, (40, 65, 65), (88, 255, 255))


def _red_mask(hsv: np.ndarray) -> np.ndarray:
    r1 = cv2.inRange(hsv, (0, 65, 65), (10, 255, 255))
    r2 = cv2.inRange(hsv, (170, 65, 65), (180, 255, 255))
    return cv2.bitwise_or(r1, r2)


def find_main_green_box(frame: np.ndarray) -> tuple[int, int, int, int] | None:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    green = _green_mask(hsv)
    green = cv2.morphologyEx(green, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cnts, _ = cv2.findContours(green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    best_area = 0
    for c in cnts:
        x, y, bw, bh = cv2.boundingRect(c)
        area = bw * bh
        if area < 400 or bw < 8 or bh < 8:
            continue
        if area > best_area:
            best_area = area
            best = (x, y, bw, bh)
    return best


def tracking_text_mask(
    h: int, w: int, box: tuple[int, int, int, int]
) -> np.ndarray:
    """Inpaint Pred/GT chips and sequence IDs hugging the tracker box."""
    x, y, bw, bh = box
    mask = np.zeros((h, w), np.uint8)
    top_band = max(12, min(30, int(bh * 0.24)))
    cv2.rectangle(mask, (max(0, x - 4), max(0, y)), (min(w, x + bw + 4), y + top_band), 255, -1)
    below = max(10, min(22, int(bh * 0.55)))
    cv2.rectangle(
        mask,
        (max(0, x - 8), max(0, y + bh - 2)),
        (min(w, x + bw + max(120, bw * 4)), min(h, y + bh + below)),
        255,
        -1,
    )
    cv2.rectangle(
        mask,
        (min(w - 1, x + bw - 2), max(0, y)),
        (min(w, x + bw + max(100, bw * 3)), min(h, y + bh + below)),
        255,
        -1,
    )
    return mask


def build_label_mask(frame: np.ndarray) -> np.ndarray:
    """Mask HUD corners and small Pred/GT text chips — not full target boxes."""
    h, w = frame.shape[:2]
    mask = corner_hud_mask(h, w)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for binary in (_green_mask(hsv), _red_mask(hsv)):
        cnts, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, y, bw, bh = cv2.boundingRect(c)
            area = bw * bh
            if area < 1400 or (bh <= 32 and bw <= 120):
                cv2.rectangle(mask, (x, y), (x + bw, y + bh), 255, -1)

    kernel = np.ones((3, 3), np.uint8)
    return cv2.dilate(mask, kernel, iterations=1)


def green_pixels_in_box(frame: np.ndarray, box: tuple[int, int, int, int]) -> np.ndarray:
    x, y, bw, bh = box
    pad = 2
    x0 = max(0, x - pad)
    y0 = max(0, y - pad)
    x1 = min(frame.shape[1], x + bw + pad)
    y1 = min(frame.shape[0], y + bh + pad)
    roi = frame[y0:y1, x0:x1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    g = _green_mask(hsv)
    out = np.zeros(frame.shape[:2], np.uint8)
    out[y0:y1, x0:x1] = g
    return out


def clean_frame(frame: np.ndarray, *, normalize_box: bool = False) -> np.ndarray:
    box = find_main_green_box(frame)
    h, w = frame.shape[:2]
    mask = build_label_mask(frame)

    if box is not None:
        mask = cv2.bitwise_or(mask, tracking_text_mask(h, w, box))

    if normalize_box and box is not None:
        mask = cv2.bitwise_or(mask, green_pixels_in_box(frame, box))

    cleaned = cv2.inpaint(frame, mask, inpaintRadius=4, flags=cv2.INPAINT_TELEA)

    if normalize_box and box is not None:
        x, y, bw, bh = box
        cv2.rectangle(
            cleaned,
            (x, y),
            (x + bw, y + bh),
            PRED_BOX_COLOR,
            PRED_BOX_THICKNESS,
        )
    return cleaned


def clean_video_file(src: str, dst: str, *, normalize_box: bool = False) -> int:
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {src}")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 15.0)
    frames_rgb: list[np.ndarray] = []

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        cleaned = clean_frame(frame, normalize_box=normalize_box)
        frames_rgb.append(cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB))

    cap.release()

    if not frames_rgb:
        raise RuntimeError(f"No frames read from {src}")

    _write_h264(dst, frames_rgb, fps)
    return len(frames_rgb)


def transcode_for_browser(src: str, dst: str) -> int:
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {src}")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 15.0)
    frames_rgb: list[np.ndarray] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames_rgb.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    cap.release()

    if not frames_rgb:
        raise RuntimeError(f"No frames read from {src}")

    _write_h264(dst, frames_rgb, fps)
    return len(frames_rgb)


def _write_h264(dst: str, frames_rgb: list[np.ndarray], fps: float) -> None:
    iio.imwrite(
        dst,
        frames_rgb,
        fps=fps,
        codec="libx264",
        pixelformat="yuv420p",
        macro_block_size=1,
        output_params=["-movflags", "+faststart"],
    )

import os
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import Response, StreamingResponse

CHUNK_SIZE = 1024 * 1024


def parse_range(range_header: str | None, file_size: int) -> tuple[int, int] | None:
    if not range_header:
        return None
    if not range_header.strip().lower().startswith("bytes="):
        return None
    spec = range_header.strip()[6:]
    if "," in spec:
        return None
    parts = spec.split("-", 1)
    if len(parts) != 2:
        return None
    start_s, end_s = parts[0].strip(), parts[1].strip()
    try:
        if start_s and end_s:
            start, end = int(start_s), int(end_s)
        elif start_s:
            start, end = int(start_s), file_size - 1
        elif end_s:
            suffix = int(end_s)
            start = max(file_size - suffix, 0)
            end = file_size - 1
        else:
            return None
    except ValueError:
        return None

    if start < 0 or end >= file_size or start > end:
        raise HTTPException(status_code=416, detail="Range not satisfiable")
    return start, end


def stream_file(path: Path, range_header: str | None) -> Response:
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Video not found")

    file_size = path.stat().st_size
    byte_range = parse_range(range_header, file_size)

    if byte_range is None:
        def full_iter():
            with path.open("rb") as f:
                while chunk := f.read(CHUNK_SIZE):
                    yield chunk

        return StreamingResponse(
            full_iter(),
            media_type="video/mp4",
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
                "Cache-Control": "public, max-age=3600",
            },
        )

    start, end = byte_range
    content_length = end - start + 1

    def partial_iter():
        with path.open("rb") as f:
            f.seek(start)
            remaining = content_length
            while remaining > 0:
                read_size = min(CHUNK_SIZE, remaining)
                data = f.read(read_size)
                if not data:
                    break
                remaining -= len(data)
                yield data

    return StreamingResponse(
        partial_iter(),
        status_code=206,
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Content-Length": str(content_length),
            "Cache-Control": "public, max-age=3600",
        },
    )

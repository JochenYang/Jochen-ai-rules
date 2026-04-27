from __future__ import annotations

import locale
from pathlib import Path


DEFAULT_TEXT_ENCODINGS = (
    'utf-8-sig',
    'utf-8',
    'gb18030',
)


def iter_candidate_encodings(extra_encodings: list[str] | tuple[str, ...] | None = None) -> list[str]:
    candidates: list[str] = []
    seen = set()

    locale_preferred = locale.getpreferredencoding(False)
    ordered = [
        *(extra_encodings or []),
        locale_preferred,
        *DEFAULT_TEXT_ENCODINGS,
    ]

    for encoding in ordered:
        if not encoding:
            continue
        normalized = encoding.strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        candidates.append(encoding)

    return candidates


def decode_text_bytes(
    payload: bytes | bytearray | memoryview | str | None,
    *,
    extra_encodings: list[str] | tuple[str, ...] | None = None,
    fallback_errors: str | None = None,
) -> tuple[str | None, str | None]:
    if payload is None:
        return None, None
    if isinstance(payload, str):
        return payload, None

    raw_payload = bytes(payload)
    for encoding in iter_candidate_encodings(extra_encodings):
        try:
            return raw_payload.decode(encoding), encoding
        except UnicodeDecodeError:
            continue

    if fallback_errors:
        return raw_payload.decode('utf-8', errors=fallback_errors), f'utf-8:{fallback_errors}'
    return None, None


def read_text_file_with_fallback(
    path: Path,
    *,
    max_bytes: int | None = None,
    extra_encodings: list[str] | tuple[str, ...] | None = None,
) -> tuple[str | None, str | None]:
    try:
        raw_payload = path.read_bytes()
    except Exception:
        return None, None

    if max_bytes is not None and len(raw_payload) > max_bytes:
        return None, None

    return decode_text_bytes(raw_payload, extra_encodings=extra_encodings)

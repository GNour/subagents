"""Canonical JSON serialization and atomic writes shared by ``lock`` and ``generate``.

One serialization is used for both writing committed assets and byte-comparing them in
``--check`` mode, so determinism holds regardless of who regenerates.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def canonical_json(data: object) -> str:
    """Deterministic pretty JSON: sorted keys, UTF-8, trailing newline."""
    return (
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    )


def write_text_atomic(path: str | Path, text: str) -> None:
    """Write ``text`` via a sibling temp file, fsync, then ``os.replace``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def write_json_atomic(path: str | Path, data: object) -> None:
    write_text_atomic(path, canonical_json(data))

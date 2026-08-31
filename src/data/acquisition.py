"""Small, version-aware download and source-manifest helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
import re
import shutil
import time
from typing import Any, Callable
from urllib.request import Request, urlopen

from .homicide_config import RAW_MANIFEST, REPO_ROOT


USER_AGENT = "econ-cost-crime-research/1.0 (official-data acquisition)"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_manifest() -> dict[str, Any]:
    if not RAW_MANIFEST.exists():
        return {"schema_version": 1, "sources": {}}
    return json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))


def _save_manifest(manifest: dict[str, Any]) -> None:
    RAW_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    temp = RAW_MANIFEST.with_suffix(".json.tmp")
    temp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(RAW_MANIFEST)


def annotate_manifest_source(source_id: str, *, status: str, note: str) -> None:
    """Add a non-destructive diagnostic annotation to an already retained source."""

    manifest = _load_manifest()
    source = manifest.get("sources", {}).get(source_id)
    if source is None:
        return
    source["status"] = status
    existing = str(source.get("notes", ""))
    if note not in existing:
        source["notes"] = f"{existing} {note}".strip()
    _save_manifest(manifest)


def retain_download(
    *,
    source_id: str,
    url: str,
    target: Path,
    institution: str,
    database: str,
    release: str,
    years: list[int] | None,
    notes: str,
    timeout: int = 180,
    validator: Callable[[Path], bool] | None = None,
) -> Path:
    """Download once, retain the vintage, checksum it, and never overwrite silently."""

    target.parent.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()
    sources = manifest.setdefault("sources", {})
    if target.exists():
        if validator is not None and not validator(target):
            raise RuntimeError(f"Retained raw file fails its format validation: {target}")
        digest = sha256(target)
        existing = sources.get(source_id)
        if existing and existing.get("sha256") != digest:
            raise RuntimeError(
                f"Retained raw file differs from its manifest and will not be overwritten: {target}"
            )
        if not existing:
            sources[source_id] = _manifest_entry(
                url=url,
                target=target,
                institution=institution,
                database=database,
                release=release,
                years=years,
                notes=notes,
                digest=digest,
            )
            _save_manifest(manifest)
        else:
            retained_path = str(target.relative_to(REPO_ROOT)).replace("\\", "/")
            if existing.get("local_path") != retained_path:
                existing["local_path"] = retained_path
                existing["bytes"] = target.stat().st_size
                _save_manifest(manifest)
        print(f"RETAINED {target.relative_to(REPO_ROOT)} sha256={digest}")
        return target

    temp = target.with_suffix(target.suffix + ".part")
    last_error: Exception | None = None
    expected_total: int | None = None
    for attempt in range(1, 13):
        offset = temp.stat().st_size if temp.exists() else 0
        headers = {"User-Agent": USER_AGENT}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                status = int(getattr(response, "status", response.getcode()))
                if offset and status != 206:
                    temp.unlink(missing_ok=True)
                    offset = 0
                content_range = response.headers.get("Content-Range", "")
                match = re.search(r"/(\d+)$", content_range)
                if match:
                    expected_total = int(match.group(1))
                elif response.headers.get("Content-Length"):
                    expected_total = offset + int(response.headers["Content-Length"])
                mode = "ab" if offset and status == 206 else "wb"
                with temp.open(mode) as output:
                    before = output.tell()
                    if before != offset:
                        raise RuntimeError(
                            f"Resume offset mismatch for {temp}: file={before}, request={offset}"
                        )
                    shutil.copyfileobj(response, output, length=1024 * 1024)
            actual = temp.stat().st_size
            if expected_total is not None and actual != expected_total:
                raise RuntimeError(
                    f"Incomplete response for {url}: received {actual} of {expected_total} bytes"
                )
            if validator is not None and not validator(temp):
                raise RuntimeError(f"Downloaded file fails its format validation: {temp}")
            last_error = None
            break
        except Exception as exc:  # pragma: no cover - network-dependent branch
            last_error = exc
            if attempt < 12:
                time.sleep(min(2**attempt, 15))
    if last_error is not None:
        raise RuntimeError(f"Could not download {url}: {last_error}") from last_error
    temp.replace(target)
    digest = sha256(target)
    sources[source_id] = _manifest_entry(
        url=url,
        target=target,
        institution=institution,
        database=database,
        release=release,
        years=years,
        notes=notes,
        digest=digest,
    )
    _save_manifest(manifest)
    print(
        f"DOWNLOADED {target.relative_to(REPO_ROOT)} bytes={target.stat().st_size} sha256={digest}"
    )
    return target


def _manifest_entry(
    *,
    url: str,
    target: Path,
    institution: str,
    database: str,
    release: str,
    years: list[int] | None,
    notes: str,
    digest: str,
) -> dict[str, Any]:
    return {
        "institution": institution,
        "database": database,
        "url": url,
        "access_date": date.today().isoformat(),
        "release_or_vintage": release,
        "years": years,
        "local_path": str(target.relative_to(REPO_ROOT)).replace("\\", "/"),
        "bytes": target.stat().st_size,
        "sha256": digest,
        "notes": notes,
    }

import argparse
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # pragma: no cover
    Image = None

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE_ROOT = Path(r"F:\Мой диск")
DEFAULT_MIRROR_ROOT = PROJECT_ROOT / "apostille-mirror" / "google-drive-mirror"
DEFAULT_PREVIEW_ROOT = PROJECT_ROOT / "apostille-mirror" / "pdf-previews"
MAX_FILES = 120

ALLOWED_DIR_HINTS = (
    "actual",
    "актуал",
    "актуализированная",
    "A©torVault",
    "A©tor-Shared",
    "A©t0r",
)


def normalize_rel_path(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    cleaned = []
    for part in rel.parts:
        sanitized = part.replace("/", "_").replace("\\", "_")
        sanitized = sanitized.replace("\x00", "")
        sanitized = sanitized.replace("*", "_")
        sanitized = sanitized.replace("?", "_")
        sanitized = sanitized.replace("\"", "_")
        sanitized = sanitized.replace("<", "_")
        sanitized = sanitized.replace(">", "_")
        sanitized = sanitized.replace("|", "_")
        sanitized = sanitized.replace(":", "_")
        sanitized = re.sub(r"[\r\n]+", "_", sanitized)
        sanitized = sanitized.strip(".")
        cleaned.append(sanitized)
    return str(Path(*cleaned))


def ensure_allowed_roots(root: Path):
    candidates = []
    if not root.exists():
        return candidates
    for child in root.iterdir():
        if child.is_dir() and any(hint.lower() in child.name.lower() for hint in ALLOWED_DIR_HINTS):
            candidates.append(child)
    if not candidates:
        for child in root.iterdir():
            if child.is_dir() and any(token in child.name.lower() for token in ("actual", "актуал", "атор")):
                candidates.append(child)
    return sorted(set(candidates), key=lambda p: p.name.casefold())


def find_pdf_paths(root: Path):
    discovered = []
    for candidate in ensure_allowed_roots(root):
        for pdf in sorted(candidate.rglob("*.pdf"), key=lambda p: p.as_posix().lower()):
            if any(token in str(pdf).lower() for token in ("quarantine", "isolated", ".git")):
                continue
            discovered.append(pdf)
    unique = []
    seen = set()
    for item in discovered:
        key = item.resolve().as_posix().lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:MAX_FILES]


def preview_placeholder(output_path: Path):
    if Image is None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"")
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1600, 2200), color=(9, 16, 25))
    draw = ImageDraw.Draw(image)
    draw.rectangle((60, 60, 1540, 2140), outline=(0, 184, 232), width=4)
    draw.text((120, 260), "PDF PREVIEW", fill=(255, 255, 255), font=None)
    draw.text((120, 1220), "Google Drive mirror", fill=(0, 184, 232), font=None)
    image.save(output_path, "JPEG", quality=92)
    return True


def render_pdf_preview(pdf_path: Path, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import pypdfium2

        pdf = pypdfium2.PdfDocument(str(pdf_path))
        page = pdf[0]
        bitmap = page.render(scale=2.0)
        pil_image = bitmap.to_pil()
        pil_image.save(output_path, "JPEG", quality=95)
        return True
    except Exception:
        return preview_placeholder(output_path)


def copy_pdf_and_preview(pdf_path: Path, source_root: Path, mirror_root: Path, preview_root: Path):
    rel = normalize_rel_path(pdf_path, source_root)
    destination = mirror_root / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or destination.stat().st_size != pdf_path.stat().st_size:
        shutil.copy2(pdf_path, destination)
    preview = preview_root / Path(rel).with_suffix(".jpg")
    if not preview.exists() or preview.stat().st_size == 0:
        render_pdf_preview(pdf_path, preview)
    return {
        "source": str(pdf_path),
        "mirror": str(destination),
        "preview": str(preview),
        "relative": rel,
        "size_bytes": pdf_path.stat().st_size,
    }


def build_gallery_page(entries):
    gallery = []
    for entry in entries:
        rel = entry["relative"]
        preview_rel = Path(rel).with_suffix(".jpg").as_posix()
        pdf_rel = rel
        page = f'''
        <article class="card">
          <div class="thumb"><img src="pdf-previews/{preview_rel}" alt="{rel}" /></div>
          <h3>{Path(rel).name}</h3>
          <div class="meta">{entry["size_bytes"]} bytes</div>
          <div class="actions">
            <a href="google-drive-mirror/{pdf_rel}" target="_blank" rel="noreferrer">Open PDF</a>
            <a href="pdf-previews/{preview_rel}" target="_blank" rel="noreferrer">High-quality preview</a>
          </div>
        </article>
        '''
        gallery.append(page)

    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Google Drive Mirror Gallery</title>
  <style>
    body {{ font-family: Arial, sans-serif; background:#071421; color:#dfeef8; margin:0; padding:24px; }}
    h1 {{ color:#7ad8ff; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:18px; }}
    .card {{ background:#0d1d2b; border:1px solid #173f59; padding:12px; border-radius:10px; }}
    .thumb {{ background:#0b1725; border:1px solid #173f59; padding:8px; margin-bottom:12px; min-height:200px; display:flex; align-items:center; justify-content:center; }}
    img {{ max-width:100%; max-height:220px; object-fit:contain; border-radius:8px; }}
    .meta {{ color:#9bb6ca; font-size:12px; margin:6px 0 12px; }}
    .actions {{ display:flex; gap:10px; flex-wrap:wrap; }}
    a {{ color:#7ad8ff; text-decoration:none; }}
    .badge {{ display:inline-block; background:#123b4d; color:#7ad8ff; padding:6px 8px; border-radius:999px; font-size:12px; margin-bottom:12px; }}
  </style>
</head>
<body>
  <h1>Google Drive Mirror Gallery</h1>
  <div class="badge">{len(entries)} mirrored PDFs</div>
  <div class="grid">
    {''.join(gallery) if gallery else '<p>No mirrored PDFs yet.</p>'}
  </div>
</body>
</html>
'''
    return html


def write_manifest(entries, source_root: Path, mirror_root: Path):
    manifest_path = mirror_root / "manifest.json"
    manifest = {
        "sourceRoot": str(source_root),
        "lastSync": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def run_cycle(source_root: Path, mirror_root: Path, preview_root: Path):
    source_root = source_root.resolve()
    pdfs = find_pdf_paths(source_root)
    entries = []
    for pdf in pdfs:
        entries.append(copy_pdf_and_preview(pdf, source_root, mirror_root, preview_root))
    manifest_path = write_manifest(entries, source_root, mirror_root)
    gallery_html = build_gallery_page(entries)
    gallery_path = PROJECT_ROOT / "apostille-mirror" / "google-drive-mirror.html"
    gallery_path.write_text(gallery_html, encoding="utf-8")
    return {"count": len(entries), "manifest": str(manifest_path), "gallery": str(gallery_path)}


def parse_args():
    parser = argparse.ArgumentParser(description="Sync approved Google Drive evidence into a mirror and produce PDF previews.")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT), help="Root of the mounted Google Drive evidence tree.")
    parser.add_argument("--mirror-root", default=str(DEFAULT_MIRROR_ROOT), help="Destination mirror root in the local repo.")
    parser.add_argument("--watch", action="store_true", help="Repeat the sync cycle every interval.")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between watch cycles.")
    parser.add_argument("--once", action="store_true", help="Run single cycle only.")
    return parser.parse_args()


def main():
    args = parse_args()
    source_root = Path(args.source_root)
    mirror_root = Path(args.mirror_root)
    preview_root = DEFAULT_PREVIEW_ROOT
    mirror_root.mkdir(parents=True, exist_ok=True)
    preview_root.mkdir(parents=True, exist_ok=True)

    if args.watch:
        while True:
            status = run_cycle(source_root, mirror_root, preview_root)
            print(f"[mirror] synced {status['count']} PDFs @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(args.interval)
        return 0

    status = run_cycle(source_root, mirror_root, preview_root)
    print(json.dumps({"status": "ok", "pdf_count": status["count"], "manifest": status["manifest"], "gallery": status["gallery"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

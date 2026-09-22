#!/usr/bin/env python3
"""Build offline PDF histories with images for Freeman-sourced waypoints."""

from pathlib import Path
from urllib.parse import urljoin, urlparse
import argparse
import csv
import hashlib
import re
import time
import urllib.request
from typing import Optional

from lxml import html as lxml_html
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer
from build_packs import assign_waypoint_ids, waypoint_id

ROOT = Path(__file__).resolve().parents[1]
COORDS = re.compile(r"^\s*(-?\d{1,2}(?:\.\d+)?)\s*,\s*(-?\d{1,3}(?:\.\d+)?)\b")


def source_id(state: str, url: str, lat: str, lon: str) -> str:
    return hashlib.sha1(f"{state}|{url}|{lat}|{lon}".encode()).hexdigest()[:10].upper()


def download(url: str, path: Path) -> Optional[Path]:
    if path.exists(): return path
    candidates = [url]
    archived = re.search(r"/web/[^/]+/(https?://.+)$", url)
    if archived:
        # Wayback image endpoints sometimes return 404/503 even when the
        # original image remains available on Airfields-Freeman.
        candidates.append(archived.group(1))
    last_error: Optional[Exception] = None
    for candidate in candidates:
        try:
            req = urllib.request.Request(candidate, headers={"User-Agent": "HistoricalAirportsForeFlight/1.0 (informational project)"})
            with urllib.request.urlopen(req, timeout=120) as response: content = response.read()
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(content); time.sleep(0.2)
            return path
        except Exception as exc:
            last_error = exc
    print(f"  image skipped: {url} ({last_error})")
    return None


def page_entries(state: str, url: str, html_path: Path):
    document = lxml_html.fromstring(html_path.read_bytes())
    blocks = document.xpath("//p | //h1 | //h2 | //h3 | //h4")
    starts = []
    for i, block in enumerate(blocks):
        if block.xpath(".//img"):
            continue
        match = COORDS.match(re.sub(r"\s+", " ", block.text_content()).strip())
        if match: starts.append((i, match.groups()))
    for pos, (index, (lat, lon)) in enumerate(starts):
        end = starts[pos + 1][0] - 1 if pos + 1 < len(starts) else len(blocks)
        title_block = blocks[index - 1] if index else blocks[index]
        title = re.sub(rf",\s*{state}$", "", re.sub(r"\s+", " ", title_block.text_content()).strip(), flags=re.I)
        yield source_id(state, url, lat, lon), title, lat, lon, blocks[index:end]


def clean_text(block) -> str:
    text = re.sub(r"\s+", " ", block.text_content()).strip()
    if re.fullmatch(r"[_\-–—\s]+", text): return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_pdf(output: Path, title: str, lat: str, lon: str, url: str, blocks, image_cache: Path) -> int:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER,
                              textColor=colors.HexColor("#263238"), spaceAfter=10))
    styles.add(ParagraphStyle(name="Caption", parent=styles["BodyText"], fontSize=8.5,
                              leading=11, textColor=colors.HexColor("#455A64"), spaceAfter=8))
    story = [Paragraph(title, styles["TitleCenter"]),
             Paragraph(f"Historical airfield - {lat}, {lon}", styles["Heading3"]),
             Paragraph("Informational and recreational reference only. Not for navigation, landing, or operational use.", styles["Caption"]),
             Paragraph(f'Source: <link href="{url}" color="#1565C0">Abandoned &amp; Little-Known Airfields</link> '
                       "by Paul Freeman. Reproduced with permission; original contributor credits are retained below.", styles["Caption"]),
             Spacer(1, 6)]
    image_count = 0
    for block in blocks:
        for tag in block.xpath(".//img"):
            src = tag.get("src")
            if not src: continue
            image_url = urljoin(url, src)
            suffix = Path(urlparse(image_url).path).suffix.lower() or ".jpg"
            local = image_cache / (hashlib.sha1(image_url.encode()).hexdigest() + suffix)
            if not download(image_url, local): continue
            try:
                with PILImage.open(local) as im: width, height = im.size
                # Leave enough vertical room for the title, safety notice,
                # source credit, and a caption on an opening page. An 8-inch
                # image could otherwise be deferred and leave page one empty.
                max_w, max_h = 6.8 * inch, 7.0 * inch
                scale = min(max_w / width, max_h / height, 1.0)
                story.extend([Spacer(1, 6), Image(str(local), width=width * scale, height=height * scale), Spacer(1, 6)])
                image_count += 1
            except Exception as exc: print(f"  unreadable image skipped: {local} ({exc})")
        text = clean_text(block)
        if text and not COORDS.match(text): story.append(Paragraph(text, styles["BodyText"])); story.append(Spacer(1, 5))
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=letter, rightMargin=0.55*inch, leftMargin=0.55*inch,
                            topMargin=0.55*inch, bottomMargin=0.55*inch,
                            title=title, author="Paul Freeman / Historical Airports Project")
    doc.build(story)
    return image_count


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--limit", type=int)
    p.add_argument("--output", type=Path, default=ROOT / "data/rich_docs")
    p.add_argument("--force", action="store_true", help="rebuild PDFs that already exist")
    args = p.parse_args(); state = args.state.upper()
    review_path = ROOT / "data/freeman_review.csv"
    with review_path.open(newline="", encoding="utf-8-sig") as f:
        state_rows = [r for r in csv.DictReader(f) if r["state"] == state and r["include"].lower() in {"yes", "true", "1", "y"}]
    assign_waypoint_ids(state, state_rows)
    wanted = {r["source_id"]: r for r in state_rows}
    pages = sorted({r["source_url"] for r in wanted.values()})
    made = 0
    processed_ids: set[str] = set()
    for url in pages:
        html_path = ROOT / "data/source/freeman" / state / Path(urlparse(url).path).name
        for ident, title, lat, lon, blocks in page_entries(state, url, html_path):
            if ident not in wanted or ident in processed_ids: continue
            processed_ids.add(ident)
            output = args.output / state / f"{waypoint_id(wanted[ident])}.pdf"
            if output.exists() and output.stat().st_size > 1024 and output.read_bytes()[:5] == b"%PDF-" and not args.force:
                made += 1
                print(f"{output.name}: already complete", flush=True)
                if args.limit and made >= args.limit: print(f"Found {made} documents", flush=True); return
                continue
            images = make_pdf(output, title, lat, lon, url, blocks, ROOT / "data/source/freeman/images")
            made += 1; print(f"{output.name}: {images} images", flush=True)
            if args.limit and made >= args.limit: print(f"Processed {made} documents", flush=True); return
    print(f"Processed {made} documents", flush=True)


if __name__ == "__main__": main()

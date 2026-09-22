#!/usr/bin/env python3
"""Collect airport names and coordinates from Airfields-Freeman state pages."""

from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError, URLError
import argparse
import csv
import hashlib
import re
import time
import urllib.request
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.airfields-freeman.com"
STATES = "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()
FIELDS = ["source_id", "source_ident", "state", "name", "historical_name", "municipality",
          "latitude_deg", "longitude_deg", "elevation_ft", "status", "include", "notes", "source_url"]
COORDS = re.compile(r"^\s*(-?\d{1,2}(?:\.\d+)?)\s*,\s*(-?\d{1,3}(?:\.\d+)?)\b")


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.text: list[str] = []
        self.blocks: list[str] = []
        self._block_parts: list[str] | None = None
        self._block_has_image = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"p", "h1", "h2", "h3", "h4"}:
            self._block_parts = []
            self._block_has_image = False
        elif tag.lower() == "img" and self._block_parts is not None:
            self._block_has_image = True
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href: self.links.append(href)

    def handle_data(self, data):
        value = re.sub(r"\s+", " ", data).strip()
        if value:
            self.text.append(value)
        if self._block_parts is not None: self._block_parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() in {"p", "h1", "h2", "h3", "h4"} and self._block_parts is not None:
            value = re.sub(r"\s+", " ", "".join(self._block_parts)).strip()
            # Airport coordinates appear in their own text block. Numbers in
            # image captions can describe unrelated places and must not create
            # extra waypoints.
            if value and not self._block_has_image: self.blocks.append(value)
            self._block_parts = None
            self._block_has_image = False


def fetch(url: str, cache: Path) -> Optional[str]:
    if cache.exists(): return cache.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": "HistoricalAirportsForeFlight/1.0 (informational project)"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                content = response.read()
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(content)
            time.sleep(0.35)
            return content.decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError) as exc:
            if attempt == 2:
                print(f"WARN: source fetch failed ({url}): {exc}")
            else:
                time.sleep(2 ** attempt)
    return None


def parse(html: str) -> PageParser:
    parser = PageParser(); parser.feed(html); return parser


def regional_urls(state: str, cache_dir: Path) -> list[str]:
    index_url = f"{BASE}/{state}/Airfields_{state}.htm"
    index_html = fetch(index_url, cache_dir / state / f"Airfields_{state}.htm")
    if index_html is None:
        return []
    parser = parse(index_html)
    found = {urljoin(index_url, href.split("#", 1)[0]) for href in parser.links}
    prefix = f"/Airfields_{state}"
    urls = [u for u in found if urlparse(u).path.startswith(f"/{state}{prefix}") and urlparse(u).path.lower().endswith((".htm", ".html"))]
    return sorted(set(urls) | {index_url})


def stable_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    """Identify an airfield without making its page URL part of its identity."""
    name = re.sub(r"[^a-z0-9]+", " ", row["name"].casefold()).strip()
    lat = f"{float(row['latitude_deg']):.4f}"
    lon = f"{float(row['longitude_deg']):.4f}"
    return row["state"], name, lat, lon


def extract_page(state: str, url: str, html: str) -> list[dict[str, str]]:
    nodes = parse(html).blocks
    rows = []
    for index, text in enumerate(nodes):
        match = COORDS.match(text)
        if not match: continue
        lat, lon = match.groups()
        if not (-90 <= float(lat) <= 90 and -180 <= float(lon) <= 180): continue
        title = ""
        for candidate in reversed(nodes[max(0, index - 8):index]):
            if re.search(rf",\s*{state}$", candidate, re.I):
                title = re.sub(rf",\s*{state}$", "", candidate, flags=re.I).strip()
                break
        if not title: continue
        municipality = title.rsplit(",", 1)[1].strip() if "," in title else ""
        name = title.rsplit(",", 1)[0].strip() if municipality else title
        digest = hashlib.sha1(f"{state}|{url}|{lat}|{lon}".encode()).hexdigest()[:10].upper()
        rows.append({
            "source_id": digest, "source_ident": "", "state": state, "name": name,
            "historical_name": "", "municipality": municipality, "latitude_deg": lat,
            "longitude_deg": lon, "elevation_ft": "", "status": "HISTORICAL_INFORMATIONAL",
            "include": "yes", "notes": "", "source_url": url,
        })
    return rows


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--state", action="append", help="state code; repeatable (default: AZ)")
    p.add_argument("--all-states", action="store_true")
    p.add_argument("--refresh", action="store_true", help="redownload cached source pages")
    p.add_argument("--output", type=Path, default=ROOT / "data/freeman_review.csv")
    args = p.parse_args()
    states = STATES if args.all_states else [s.upper() for s in (args.state or ["AZ"])]
    cache_dir = ROOT / "data/source/freeman"
    if args.refresh:
        for state in states:
            state_dir = cache_dir / state
            if state_dir.exists():
                for path in state_dir.glob("*.htm*"): path.unlink()
    existing = {}
    if args.output.exists():
        with args.output.open(newline="", encoding="utf-8-sig") as f:
            existing = {r["source_id"]: r for r in csv.DictReader(f)}
    retained = [r for r in existing.values() if r["state"] not in states]
    failed_states: set[str] = set()
    failed_urls: set[str] = set()
    collected = []
    for state in states:
        urls = regional_urls(state, cache_dir)
        if not urls:
            failed_states.add(state)
            print(f"{state}: source index unavailable; retained existing records")
            continue
        state_rows = []
        for url in urls:
            filename = Path(urlparse(url).path).name
            html = fetch(url, cache_dir / state / filename)
            if html is not None:
                state_rows.extend(extract_page(state, url, html))
            else:
                failed_urls.add(url)
        unique = {stable_key(r): r for r in state_rows}
        prior_by_key = {stable_key(r): r for r in existing.values() if r["state"] == state}
        merged = {}
        for key, row in unique.items():
            prior = prior_by_key.get(key, {})
            # Keep the reviewed record identity stable when a source page moves.
            row["source_id"] = prior.get("source_id", row["source_id"])
            for field in ("historical_name", "include", "notes"):
                if prior.get(field, ""): row[field] = prior[field]
            merged[row["source_id"]] = row
        collected.extend(merged.values())
        print(f"{state}: {len(urls)} pages, {len(merged)} airfields")
    collected_ids = {r["source_id"] for r in collected}
    retained.extend(
        r for r in existing.values()
        if r["state"] in failed_states
        or (r["source_url"] in failed_urls and r["source_id"] not in collected_ids)
    )
    rows = retained + collected
    rows.sort(key=lambda r: (r["state"], r["name"].casefold(), r["source_id"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    print(f"Wrote {len(rows)} records to {args.output}")


if __name__ == "__main__": main()

#!/usr/bin/env python3
"""Create state-level ForeFlight Content Packs for closed-airport candidates."""

from pathlib import Path
import argparse
import csv
import datetime as dt
import json
import re
import shutil
import zipfile
import html
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}
REVIEW_FIELDS = [
    "source_id", "source_ident", "state", "name", "historical_name", "municipality",
    "latitude_deg", "longitude_deg", "elevation_ft", "status", "include", "notes", "source_url",
]


def load_source(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [r for r in csv.DictReader(f)
                if r.get("iso_country") == "US" and r.get("type") in {"closed", "closed_airport"}]


def seed_review(source: list[dict[str, str]], review_path: Path) -> list[dict[str, str]]:
    existing = {}
    if review_path.exists():
        with review_path.open(newline="", encoding="utf-8-sig") as f:
            existing = {r["source_id"]: r for r in csv.DictReader(f)}
    rows = []
    for item in source:
        source_id = item["id"]
        prior = existing.get(source_id, {})
        state = item.get("iso_region", "").removeprefix("US-")
        row = {
            "source_id": source_id,
            "source_ident": item.get("ident", ""),
            "state": state,
            "name": item.get("name", ""),
            "historical_name": prior.get("historical_name", ""),
            "municipality": item.get("municipality", ""),
            "latitude_deg": item.get("latitude_deg", ""),
            "longitude_deg": item.get("longitude_deg", ""),
            "elevation_ft": item.get("elevation_ft", ""),
            "status": prior.get("status", "CLOSED_UNVERIFIED"),
            "include": prior.get("include", "yes"),
            "notes": prior.get("notes", ""),
            "source_url": prior.get("source_url", item.get("home_link") or item.get("wikipedia_link") or ""),
        }
        rows.append(row)
    rows.sort(key=lambda r: (r["state"], r["name"].casefold(), int(r["source_id"])))
    review_path.parent.mkdir(parents=True, exist_ok=True)
    with review_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEW_FIELDS)
        writer.writeheader(); writer.writerows(rows)
    return rows


def clean_description(row: dict[str, str]) -> str:
    label = row["historical_name"] or row["name"]
    location = row["municipality"]
    if row["status"] == "HISTORICAL_INFORMATIONAL":
        status = "Historical airfield"
    else:
        status = "Verified abandoned" if row["status"] == "ABANDONED_VERIFIED" else "Closed—unverified"
    text = f"{status}: {label}" + (f", {location}" if location else "")
    return re.sub(r"\s+", " ", text).strip()[:120]


def waypoint_id(row: dict[str, str]) -> str:
    return row.get("_waypoint_id") or f"AA_{row['state']}_{row['source_id']}"


def safe_id_part(value: str, limit: int = 42) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().upper()
    value = re.sub(r"[^A-Z0-9]+", "_", value).strip("_")
    return value[:limit].rstrip("_")


def assign_waypoint_ids(state: str, rows: list[dict[str, str]]) -> None:
    """Prefer readable IDs; disambiguate only actual name collisions."""
    used: set[str] = set()
    for row in rows:
        title = row.get("historical_name") or row["name"]
        primary_name = re.split(r"\s+/\s+", title, maxsplit=1)[0]
        base = f"{state}_{safe_id_part(primary_name)}"
        candidate = base
        if candidate in used and row.get("municipality"):
            candidate = f"{base[:34].rstrip('_')}_{safe_id_part(row['municipality'], 12)}"
        if candidate in used:
            candidate = f"{base[:37].rstrip('_')}_{row['source_id'][-6:]}"
        row["_waypoint_id"] = candidate
        used.add(candidate)


def document_name(row: dict[str, str]) -> str:
    """ForeFlight displays the filename portion following the waypoint ID."""
    title = row.get("historical_name") or row["name"]
    title = re.sub(r"[/\\:*?\"<>|]", " - ", title)
    title = re.sub(r"\s+", " ", title).strip(" .-")
    return (title[:100] or "Historical Airfield").replace(" ", "_")


def write_pack(state: str, rows: list[dict[str, str]], out_dir: Path, version: float) -> None:
    assign_waypoint_ids(state, rows)
    state_name = STATES.get(state, state)
    pack_name = f"Abandoned_Airports_{state}"
    staging = out_dir / ".staging" / pack_name
    if staging.exists(): shutil.rmtree(staging)
    navdata = staging / "navdata"; navdata.mkdir(parents=True)
    manifest = {
        "name": f"Historical Airfields - {STATES.get(state, state)}",
        "abbreviation": f"ABN-{state}", "version": version,
        "effectiveDate": dt.datetime.now().strftime("%Y%m%dT00:00:00"),
        "organizationName": "Historical Airports Project",
    }
    (staging / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    kml_ns = "http://www.opengis.net/kml/2.2"
    ET.register_namespace("", kml_ns)
    kml = ET.Element(f"{{{kml_ns}}}kml")
    document = ET.SubElement(kml, f"{{{kml_ns}}}Document")
    ET.SubElement(document, f"{{{kml_ns}}}name").text = f"Historical Airfields - {STATES.get(state, state)}"
    style = ET.SubElement(document, f"{{{kml_ns}}}Style", id="historical-airport")
    icon_style = ET.SubElement(style, f"{{{kml_ns}}}IconStyle")
    ET.SubElement(icon_style, f"{{{kml_ns}}}scale").text = "1.0"
    icon = ET.SubElement(icon_style, f"{{{kml_ns}}}Icon")
    ET.SubElement(icon, f"{{{kml_ns}}}href").text = "https://maps.google.com/mapfiles/kml/shapes/airports.png"
    for row in rows:
        placemark = ET.SubElement(document, f"{{{kml_ns}}}Placemark")
        ET.SubElement(placemark, f"{{{kml_ns}}}name").text = waypoint_id(row)
        ET.SubElement(placemark, f"{{{kml_ns}}}description").text = clean_description(row)
        ET.SubElement(placemark, f"{{{kml_ns}}}styleUrl").text = "#historical-airport"
        point = ET.SubElement(placemark, f"{{{kml_ns}}}Point")
        altitude = row.get("elevation_ft", "").strip()
        coordinates = f"{row['longitude_deg']},{row['latitude_deg']}"
        if altitude:
            coordinates += f",{float(altitude) * 0.3048:.2f}"
        ET.SubElement(point, f"{{{kml_ns}}}coordinates").text = coordinates
    layer_filename = f"{state_name.replace(' ', '_')}_Historical_Airfields.kml"
    ET.ElementTree(kml).write(navdata / layer_filename, encoding="utf-8", xml_declaration=True)
    for row in rows:
        rich_pdf = ROOT / "data/rich_docs" / state / f"{waypoint_id(row)}.pdf"
        if rich_pdf.exists():
            shutil.copy2(rich_pdf, navdata / f"{waypoint_id(row)}{document_name(row)}.pdf")
        elif row.get("source_url"):
            title = html.escape(row["historical_name"] or row["name"])
            url = html.escape(row["source_url"], quote=True)
            (navdata / f"{waypoint_id(row)}Source.txt").write_text(
                f"<h2>{title}</h2><p>Informational historical reference only.</p>"
                f"<p>Source: <a href=\"{url}\">Abandoned &amp; Little-Known Airfields</a> "
                f"by Paul Freeman.</p>", encoding="utf-8")
    layer_name = layer_filename.removesuffix(".kml")
    (navdata / "README.txt").write_text(f"""<h1>Historical Airfields - {state_name}</h1>
<p><b>Version {version:.1f} &middot; {len(rows)} historical airfields</b></p>
<p>Explore abandoned and little-known airfields through map markers and illustrated histories
available directly in ForeFlight.</p>
<p><b>For historical and recreational reference only.</b> Do not use this package for navigation,
landing, flight planning, or operational decisions.</p>

<h2>What's included</h2>
<ul>
  <li>{len(rows)} historical-airfield waypoints</li>
  <li>ForeFlight-supported airport map markers linked directly to each waypoint</li>
  <li>Readable waypoint IDs beginning with <b>{state}_</b></li>
  <li>One airport-named, illustrated PDF attached to every waypoint</li>
  <li>Offline narratives, imagery, captions, and contributor credits</li>
</ul>

<h2>Use the package</h2>
<ol>
  <li>Open Maps and enable <b>{layer_name}</b> in the map-layer selector.</li>
  <li>Tap an airport marker or search for a waypoint beginning with <b>{state}_</b>.</li>
  <li>Open the airport-named PDF from the waypoint details.</li>
</ol>
<p>Histories and images work offline. Source-page links require internet access.</p>

<h2>Important limitations</h2>
<ul>
  <li>Coordinates are historical reference points and may be approximate.</li>
  <li>A location may be abandoned, redeveloped, privately owned, restricted, hazardous, or no
  longer recognizable.</li>
  <li>The package does not provide current runway conditions, obstacles, ownership, landing
  permission, weather, NOTAMs, or airspace information.</li>
  <li>A marker does not indicate that landing is possible, safe, or permitted.</li>
</ul>

<h2>Update or remove</h2>
<p>Delete an older edition before importing a replacement. Early test editions used identifiers
beginning with <b>AA_{state}_</b> and a layer named <b>user_waypoints</b>. Neither is part of version
{version:.1f}. Remove any remaining legacy entries under More &gt; Custom Content &gt; User Waypoints.</p>
<p>To remove this edition, open More &gt; Custom Content &gt; Content Packs, select
<b>Historical Airfields - {state_name}</b>, and tap <b>Delete</b>.</p>

<h2>Credits</h2>
<p>Historical research, coordinates, narratives, and imagery: Paul Freeman's
<i>Abandoned &amp; Little-Known Airfields</i>, reproduced with permission. Individual contributor
credits are retained in the attached histories.</p>
<p>ForeFlight package compilation: Historical Airports Project.</p>
""", encoding="utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"{pack_name}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(staging.rglob("*")):
            if path.is_file(): zf.write(path, path.relative_to(staging.parent))
    print(f"{state}: {len(rows):4d} candidates -> {archive.name}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=ROOT / "data/source/airports.csv")
    p.add_argument("--review", type=Path, default=ROOT / "data/airports_review.csv")
    p.add_argument("--provider", choices=("freeman", "ourairports"), default="freeman")
    p.add_argument("--freeman-review", type=Path, default=ROOT / "data/freeman_review.csv")
    p.add_argument("--output", type=Path, help="output directory (default: dist/<provider>)")
    p.add_argument("--state", action="append", help="two-letter state; repeat as needed")
    p.add_argument("--include-nonstates", action="store_true")
    p.add_argument("--version", type=float, default=2.1)
    args = p.parse_args()
    if args.output is None:
        args.output = ROOT / "dist" / args.provider
    if args.provider == "freeman":
        if not args.freeman_review.exists(): raise SystemExit("Freeman data missing; run scripts/fetch_freeman.py first")
        with args.freeman_review.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    else:
        if not args.source.exists(): raise SystemExit("Source missing; run scripts/fetch_ourairports.py first")
        rows = seed_review(load_source(args.source), args.review)
    selected = set(s.upper() for s in args.state) if args.state else set(STATES)
    if args.include_nonstates: selected.update(r["state"] for r in rows)
    for state in sorted(selected):
        state_rows = [r for r in rows if r["state"] == state and r["include"].strip().lower() in {"1", "true", "yes", "y"}]
        write_pack(state, state_rows, args.output, args.version)


if __name__ == "__main__": main()

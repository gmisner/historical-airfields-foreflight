#!/usr/bin/env python3
"""Validate generated ZIP structure and ForeFlight waypoint constraints."""

from pathlib import Path
import csv
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"^[A-Z0-9_-]*[A-Z][A-Z0-9_-]*$")


def validate(path: Path) -> list[str]:
    errors = []
    root = path.stem + "/"
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        manifest_name = root + "manifest.json"
        csv_name = root + "navdata/user_waypoints.csv"
        kml_names = sorted(n for n in names if n.startswith(root + "navdata/") and n.lower().endswith(".kml"))
        kmz_names = sorted(n for n in names if n.startswith(root + "layers/") and n.lower().endswith(".kmz"))
        for required in (manifest_name,):
            if required not in names: errors.append(f"missing {required}")
        if csv_name not in names and not kml_names:
            errors.append("missing a navdata CSV or KML waypoint file")
        if errors: return errors
        try: json.loads(zf.read(manifest_name))
        except Exception as exc: errors.append(f"invalid manifest: {exc}")
        if kmz_names:
            with zipfile.ZipFile(io.BytesIO(zf.read(kmz_names[0]))) as kmz:
                kmz_files = set(kmz.namelist())
                if "doc.kml" not in kmz_files: errors.append("marker-layer KMZ missing doc.kml")
                if "historical-airport-marker.png" not in kmz_files:
                    errors.append("marker-layer KMZ missing custom marker PNG")
                if "doc.kml" in kmz_files:
                    layer_root = ET.fromstring(kmz.read("doc.kml"))
                    layer_ns = {"k": "http://www.opengis.net/kml/2.2"}
                    scale = layer_root.findtext(
                        ".//k:Style[@id='historical-airport']/k:IconStyle/k:scale",
                        namespaces=layer_ns,
                    )
                    href = layer_root.findtext(
                        ".//k:Style[@id='historical-airport']/k:IconStyle/k:Icon/k:href",
                        namespaces=layer_ns,
                    )
                    if scale != "0.35": errors.append(f"marker-layer scale is {scale!r}, expected '0.35'")
                    if href not in kmz_files: errors.append(f"marker-layer icon not bundled: {href!r}")
        if kml_names:
            if len(kml_names) != 1: errors.append(f"expected one navdata KML, found {len(kml_names)}")
            kml_name = kml_names[0]
            ns = {"k": "http://www.opengis.net/kml/2.2"}
            root_element = ET.fromstring(zf.read(kml_name))
            style = root_element.find(".//k:Style[@id='historical-airport']/k:IconStyle/k:Icon/k:href", ns)
            if style is None or not (style.text or "").strip(): errors.append("missing historical-airport icon style")
            elif not (style.text or "").startswith(("http://", "https://")):
                icon_name = root + "navdata/" + (style.text or "").strip()
                if icon_name not in names: errors.append(f"missing custom marker asset {icon_name}")
                elif not zf.read(icon_name).startswith(b"\x89PNG\r\n\x1a\n"):
                    errors.append(f"custom marker is not a PNG: {icon_name}")
            rows = []
            for placemark in root_element.findall(".//k:Placemark", ns):
                name = placemark.findtext("k:name", namespaces=ns) or ""
                description = placemark.findtext("k:description", namespaces=ns) or ""
                coordinates = placemark.findtext("k:Point/k:coordinates", namespaces=ns) or ""
                parts = coordinates.strip().split(",")
                rows.append([name, description, parts[1] if len(parts)>1 else "", parts[0] if parts else ""])
            reader = iter(rows)
        else:
            reader = csv.reader(io.StringIO(zf.read(csv_name).decode("utf-8")))
        seen = set()
        for line, row in enumerate(reader, 1):
            if len(row) not in {4, 5}: errors.append(f"line {line}: expected 4 or 5 columns"); continue
            ident = row[0]
            if len(ident) < 3 or not NAME.fullmatch(ident): errors.append(f"line {line}: invalid ID {ident!r}")
            if ident in seen: errors.append(f"line {line}: duplicate ID {ident}")
            seen.add(ident)
            try:
                lat, lon = float(row[2]), float(row[3])
                if not (-90 <= lat <= 90 and -180 <= lon <= 180): raise ValueError("out of range")
            except ValueError as exc: errors.append(f"line {line}: invalid coordinates ({exc})")
    return errors


def main() -> None:
    archives = sorted((ROOT / "dist").rglob("Abandoned_Airports_*.zip"))
    if not archives: raise SystemExit("No packs found in dist/")
    failures = 0
    for archive in archives:
        errors = validate(archive)
        if errors:
            failures += 1; print(f"FAIL {archive.name}: " + "; ".join(errors))
    if failures: raise SystemExit(1)
    print(f"Validated {len(archives)} content packs")


if __name__ == "__main__": main()

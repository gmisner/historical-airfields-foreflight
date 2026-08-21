#!/usr/bin/env python3
"""Prepare and optionally publish a GitHub Release containing all state packs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "freeman"
DEFAULT_REPOSITORY = "gmisner/historical-airfields-foreflight"
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


def expected_counts() -> dict[str, int]:
    counts = {state: 0 for state in STATES}
    with (ROOT / "data" / "freeman_review.csv").open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            if row.get("include", "").strip().lower() in {"1", "true", "yes", "y"}:
                counts[row["state"]] += 1
    return counts


def validate_assets() -> tuple[list[Path], dict[str, int]]:
    counts = expected_counts()
    assets: list[Path] = []
    errors: list[str] = []
    for state in sorted(STATES):
        asset = DIST / f"Abandoned_Airports_{state}.zip"
        if not asset.exists():
            errors.append(f"missing {asset.name}")
            continue
        try:
            with ZipFile(asset) as archive:
                names = archive.namelist()
                pdf_count = sum(name.lower().endswith(".pdf") for name in names)
                kml_count = sum(name.lower().endswith(".kml") for name in names)
                manifest_count = sum(name.endswith("/manifest.json") for name in names)
                if pdf_count != counts[state]:
                    errors.append(f"{state}: {pdf_count} PDFs, expected {counts[state]}")
                if kml_count != 1:
                    errors.append(f"{state}: expected one KML, found {kml_count}")
                if manifest_count != 1:
                    errors.append(f"{state}: expected one manifest, found {manifest_count}")
        except Exception as exc:
            errors.append(f"{state}: invalid ZIP: {exc}")
        assets.append(asset)
    if errors:
        raise SystemExit("Release preparation failed:\n- " + "\n- ".join(errors))
    return assets, counts


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def release_url(repository: str, tag: str, filename: str) -> str:
    return f"https://github.com/{repository}/releases/download/{tag}/{filename}"


def foreflight_url(repository: str, tag: str, filename: str) -> str:
    return "https://foreflight.com/content?downloadURL=" + quote(
        release_url(repository, tag, filename), safe=""
    )


def write_outputs(
    assets: list[Path], counts: dict[str, int], repository: str, tag: str
) -> tuple[Path, Path]:
    checksum_path = DIST / "SHA256SUMS.txt"
    checksum_path.write_text(
        "".join(f"{digest(path)}  {path.name}\n" for path in assets), encoding="utf-8"
    )
    packs_path = ROOT / "PACKS.md"
    lines = [
        "# Download ForeFlight content packs\n",
        f"Release: `{tag}` · {sum(counts.values()):,} historical airfields · 50 states\n",
        "On an iPhone or iPad with ForeFlight installed, long-press an **Install in "
        "ForeFlight** link and choose **Open in ForeFlight**. A normal ZIP link is also "
        "provided for Files, AirDrop, Finder, email, and archival downloads.\n",
        "| State | Airfields | ForeFlight | ZIP |\n",
        "| --- | ---: | --- | --- |\n",
    ]
    for state in sorted(STATES, key=lambda code: STATES[code]):
        filename = f"Abandoned_Airports_{state}.zip"
        lines.append(
            f"| {STATES[state]} | {counts[state]} | "
            f"[Install in ForeFlight]({foreflight_url(repository, tag, filename)}) | "
            f"[Download ZIP]({release_url(repository, tag, filename)}) |\n"
        )
    lines.extend(
        [
            "\n## Important\n",
            "These packs are informational and recreational historical references only. "
            "They are not suitable for navigation, landing decisions, flight planning, or "
            "operational use.\n",
            "Delete an older edition before importing a replacement to avoid retaining obsolete "
            "waypoints or layer names.\n",
            "Installation behavior follows [ForeFlight's official Content Packs guidance]"
            "(https://www.foreflight.com/support/content-packs/).\n",
        ]
    )
    packs_path.write_text("".join(lines), encoding="utf-8")
    return checksum_path, packs_path


def publish(repository: str, tag: str, assets: list[Path], checksum_path: Path) -> None:
    subprocess.run(["gh", "auth", "status", "-h", "github.com"], check=True)
    notes = ROOT / "PACKS.md"
    command = [
        "gh", "release", "create", tag,
        "--repo", repository,
        "--title", f"Historical Airfields ForeFlight Packs {tag}",
        "--notes-file", str(notes),
    ]
    command.extend(str(path) for path in [*assets, checksum_path])
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="v2.1.0")
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument(
        "--publish", action="store_true",
        help="create the GitHub Release after preparation; omitted by default",
    )
    args = parser.parse_args()
    assets, counts = validate_assets()
    checksum_path, packs_path = write_outputs(assets, counts, args.repository, args.tag)
    total_bytes = sum(path.stat().st_size for path in assets)
    print(f"Prepared {len(assets)} ZIP assets ({total_bytes / (1024 ** 3):.2f} GiB)")
    print(f"Checksums: {checksum_path}")
    print(f"Install links: {packs_path}")
    if args.publish:
        publish(args.repository, args.tag, assets, checksum_path)
    else:
        print("Dry run only; pass --publish after GitHub authentication is restored.")


if __name__ == "__main__":
    main()

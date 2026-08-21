#!/usr/bin/env python3
"""Download the current public-domain OurAirports airport snapshot."""

from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import urllib.request

URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=URL)
    parser.add_argument("--output", type=Path, default=ROOT / "data/source/airports.csv")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix(".csv.part")
    with urllib.request.urlopen(args.url, timeout=120) as response, temp.open("wb") as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)
    temp.replace(args.output)
    metadata = {
        "source_url": args.url,
        "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }
    args.output.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Downloaded {args.output} ({args.output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

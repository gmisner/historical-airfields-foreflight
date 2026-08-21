#!/usr/bin/env python3
"""Migrate hash-named rich PDFs to readable airport waypoint filenames."""

from pathlib import Path
import argparse
import csv
import re

from build_packs import ROOT, assign_waypoint_ids, waypoint_id


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    args = p.parse_args(); state = args.state.upper()
    with (ROOT / "data/freeman_review.csv").open(newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["state"] == state]
    assign_waypoint_ids(state, rows)
    folder = ROOT / "data/rich_docs" / state
    migrated = 0
    valid_old = set()
    for row in rows:
        old = folder / f"AA_{state}_{row['source_id']}History.pdf"
        valid_old.add(old.name)
        new = folder / f"{waypoint_id(row)}.pdf"
        if old.exists():
            old.replace(new); migrated += 1
    removed = 0
    old_pattern = re.compile(rf"AA_{state}_[0-9A-F]{{10}}History\.pdf$")
    for path in folder.glob("*.pdf"):
        if old_pattern.fullmatch(path.name):
            path.unlink(); removed += 1
    print(f"{state}: renamed {migrated} PDFs; removed {removed} obsolete generated PDFs")


if __name__ == "__main__": main()

# Development guide

This document contains the builder and data-maintenance information that is
not needed by people who only want to install the finished ForeFlight packs.

## Build a state pack

```sh
python3 scripts/fetch_freeman.py --state AZ
python3 scripts/build_rich_docs.py --state AZ
python3 scripts/build_packs.py --state AZ
python3 scripts/validate_packs.py
```

Outputs are written beneath `dist/<provider>/`, including
`dist/freeman/Abandoned_Airports_AZ.zip`. Each archive contains a parent folder:

```text
Abandoned_Airports_AZ/
  manifest.json
  navdata/
    Arizona_Historical_Airfields.kml
    README.txt
```

## Data workflow

- `data/source/freeman/` caches downloaded state and regional pages.
- `data/freeman_review.csv` is the durable editorial dataset. Edit `include`,
  `status`, `historical_name`, `notes`, and `source_url` there.
- Running the fetcher again retains existing editorial fields.
- `status` defaults to `HISTORICAL_INFORMATIONAL`.

Waypoint identifiers use readable state-prefixed names such as
`AZ_QUEEN_CREEK_AIRFIELD`. Every waypoint uses a ForeFlight-supported airport
KML marker and links to its attached history document.

`build_rich_docs.py` downloads authorized source images and turns each
airfield's narrative, captions, contributor credits, and imagery into an
offline PDF. If no rich PDF is available, the pack falls back to a small linked
source document.

## Nationwide and selected builds

- `python3 scripts/fetch_freeman.py --all-states` collects the 50-state dataset.
- `--include-nonstates` includes every U.S. subdivision present in the source.
- Repeat `--state AZ` with other abbreviations to build selected states.

Source elevations in feet are converted to meters for KML. Blank elevations
are permitted.

## Validation and publishing

- Run `python3 scripts/validate_packs.py` before publishing.
- Follow [TESTING.md](TESTING.md) for automated and ForeFlight device checks.
- Review [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for unavailable source images.
- Follow [RELEASING.md](RELEASING.md) to prepare checksums, installation links,
  and a versioned GitHub Release.

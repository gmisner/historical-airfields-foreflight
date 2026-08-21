![Historical Airports — ForeFlight Content Packs](.github/artwork/social-preview.png)

# Historical Airports — ForeFlight Content Packs

Builds one ForeFlight Content Pack per U.S. state from a reviewed airport CSV.

The primary source is Paul Freeman's *Abandoned & Little-Known Airfields* site,
used with the site owner's permission. Packs are informational historical
references for sightseeing and exploration—not operational aviation data.

## Quick start

```sh
python3 scripts/fetch_freeman.py --state AZ
python3 scripts/build_rich_docs.py --state AZ
python3 scripts/build_packs.py --state AZ
python3 scripts/validate_packs.py
```

Outputs are written beneath `dist/<provider>/`, including
`dist/freeman/Abandoned_Airports_AZ.zip`. Each archive contains a parent folder
with:

```text
Abandoned_Airports_AZ/
  manifest.json
  navdata/
    Arizona_Historical_Airfields.kml
    README.txt
```

AirDrop a state ZIP to an iPhone or iPad and choose ForeFlight, or import it
through Files, email, Finder, or a supported cloud document provider.

## Data workflow

- `data/source/freeman/` caches the downloaded state and regional pages.
- `data/freeman_review.csv` is generated from those pages and is the durable
  editorial dataset. Edit `include`, `status`, `historical_name`, `notes`, and
  `source_url` there.
- Run the builder again after editing. Existing editorial fields are retained
  when the source is refreshed.
- `status` defaults to `HISTORICAL_INFORMATIONAL`.

Waypoint identifiers use readable state-prefixed names such as
`AZ_QUEEN_CREEK_AIRFIELD`. Each waypoint has an airport-style KML marker and an
attached source document linking back to the relevant Airfields-Freeman page.

`build_rich_docs.py` optionally downloads the source images and turns each
airfield's narrative, captions, contributor credits, and imagery into an
offline PDF attached to its waypoint. Without a rich PDF, the pack falls back
to a small linked source document. Descriptions are intentionally short for
ForeFlight's map display.

## Scope

The default builder covers the 50 states for which data has been collected.
Use `scripts/fetch_freeman.py --all-states` to collect the nationwide dataset.
Use `--include-nonstates` to build every U.S. subdivision present in the source.
Use `--state AZ` (repeatable) to build selected states.

## Sources and limitations

- Historical airport names and coordinates: *Abandoned & Little-Known
  Airfields*, © Paul Freeman, used with permission.
- Package format: ForeFlight Content Packs with a descriptive state-specific
  KML file in `navdata/`.
- Source elevations in feet are converted to meters for KML. Blank elevations
  are allowed.

This project is historical reference material. Coordinates and status may be
wrong or stale; obstacles, ownership, and current land use are not represented.

## Support

If you find this project useful, you can buy me a whiskey.

<a href="https://www.buymeacoffee.com/thegearbox"><img src=".github/artwork/buy-me-a-whiskey.svg" alt="Buy me a whiskey" width="260" height="60"></a>

![Historical Airports — ForeFlight Content Packs](.github/artwork/social-preview.png)

# Historical Airports — ForeFlight Content Packs

Builds one ForeFlight Content Pack per U.S. state from a reviewed airport CSV.
The version 2.1 collection contains 2,803 historical airfields across all 50
states, with an airport-named illustrated PDF attached to every waypoint.

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

## Download and install

You need ForeFlight Mobile on an iPhone or iPad. Choose only the states you
want; each state is a separate Content Pack.

### Install directly on an iPhone or iPad

1. Open [the complete state list](PACKS.md) in Safari on the device.
2. Long-press **Install in ForeFlight** beside a state.
3. Choose **Open in ForeFlight**. If that choice is not shown, tap **Download
   ZIP**, open the download in Files, tap **Share**, and choose ForeFlight.
4. In ForeFlight, open **More → Custom Content** and confirm that the state pack
   appears. On the Maps page, open the map settings menu and enable the state's
   historical-airfields layer.
5. Tap a historical-airfield marker to view its name and attached offline
   illustrated history.

Keep the downloaded file as a ZIP—do not unzip it before sharing it to
ForeFlight. Delete an older edition before importing its replacement. See
[ForeFlight's official Content Packs instructions](https://www.foreflight.com/support/content-packs/)
for other transfer methods, including AirDrop, Finder, and email.

### State downloads — release v2.1.0

Each state name below downloads its ForeFlight-ready ZIP. For one-tap hosted
installation links and airfield counts, use [the complete state list](PACKS.md).

| | | | |
| --- | --- | --- | --- |
| [Alabama](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_AL.zip) | [Alaska](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_AK.zip) | [Arizona](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_AZ.zip) | [Arkansas](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_AR.zip) |
| [California](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_CA.zip) | [Colorado](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_CO.zip) | [Connecticut](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_CT.zip) | [Delaware](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_DE.zip) |
| [Florida](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_FL.zip) | [Georgia](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_GA.zip) | [Hawaii](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_HI.zip) | [Idaho](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_ID.zip) |
| [Illinois](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_IL.zip) | [Indiana](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_IN.zip) | [Iowa](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_IA.zip) | [Kansas](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_KS.zip) |
| [Kentucky](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_KY.zip) | [Louisiana](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_LA.zip) | [Maine](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_ME.zip) | [Maryland](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_MD.zip) |
| [Massachusetts](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_MA.zip) | [Michigan](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_MI.zip) | [Minnesota](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_MN.zip) | [Mississippi](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_MS.zip) |
| [Missouri](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_MO.zip) | [Montana](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_MT.zip) | [Nebraska](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_NE.zip) | [Nevada](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_NV.zip) |
| [New Hampshire](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_NH.zip) | [New Jersey](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_NJ.zip) | [New Mexico](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_NM.zip) | [New York](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_NY.zip) |
| [North Carolina](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_NC.zip) | [North Dakota](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_ND.zip) | [Ohio](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_OH.zip) | [Oklahoma](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_OK.zip) |
| [Oregon](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_OR.zip) | [Pennsylvania](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_PA.zip) | [Rhode Island](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_RI.zip) | [South Carolina](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_SC.zip) |
| [South Dakota](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_SD.zip) | [Tennessee](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_TN.zip) | [Texas](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_TX.zip) | [Utah](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_UT.zip) |
| [Vermont](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_VT.zip) | [Virginia](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_VA.zip) | [Washington](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_WA.zip) | [West Virginia](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_WV.zip) |
| [Wisconsin](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_WI.zip) | [Wyoming](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/Abandoned_Airports_WY.zip) | [Release checksums](https://github.com/gmisner/historical-airfields-foreflight/releases/download/v2.1.0/SHA256SUMS.txt) | [All release files](https://github.com/gmisner/historical-airfields-foreflight/releases/tag/v2.1.0) |

## Data workflow

- `data/source/freeman/` caches the downloaded state and regional pages.
- `data/freeman_review.csv` is generated from those pages and is the durable
  editorial dataset. Edit `include`, `status`, `historical_name`, `notes`, and
  `source_url` there.
- Run the builder again after editing. Existing editorial fields are retained
  when the source is refreshed.
- `status` defaults to `HISTORICAL_INFORMATIONAL`.

Waypoint identifiers use readable state-prefixed names such as
`AZ_QUEEN_CREEK_AIRFIELD`. Each waypoint has a ForeFlight-supported airport KML marker and an
attached source document linking back to the relevant Airfields-Freeman page.

`build_rich_docs.py` optionally downloads the source images and turns each
airfield's narrative, captions, contributor credits, and imagery into an
offline PDF attached to its waypoint. Without a rich PDF, the pack falls back
to a small linked source document. Descriptions are intentionally short for
ForeFlight's map display.

## Scope

The default builder covers all 50 states and 2,803 reviewed historical
airfields.
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

Known source images that are no longer available from their original URLs are
listed in [KNOWN_ISSUES.md](KNOWN_ISSUES.md). Every affected history retains its
complete available narrative and all other available imagery.

## Preparing a GitHub Release

Generated PDFs, source caches, and ZIP packages are deliberately excluded from
Git history. After building and validating all states, prepare release assets,
checksums, and installation links with:

```sh
python3 scripts/prepare_release.py --tag v2.1.0
```

The command is a dry run by default. Once `gh auth status` succeeds and the
repository exists, publish all 50 state ZIPs and `SHA256SUMS.txt` with:

```sh
python3 scripts/prepare_release.py --tag v2.1.0 --publish
```

See [RELEASING.md](RELEASING.md) for the one-time repository setup and final
ForeFlight verification checklist.

## Support

If you find this project useful, you can buy me a whiskey.

<a href="https://www.buymeacoffee.com/thegearbox"><img src=".github/artwork/buy-me-a-whiskey.svg" alt="Buy me a whiskey" width="260" height="60"></a>

Paul Freeman's *Abandoned &amp; Little-Known Airfields* is the primary data source
for this project. If you value his research, please consider
[making a donation to Paul Freeman via PayPal](https://www.paypal.com/donate?token=zsWj6HRO7zWA8JSw2DWV0Ujuj-bJlrW-RaMRNoZU6Z9rxL_I4rgMbI_vyf9pQiUYtLJWBm0yJ149qAoi).

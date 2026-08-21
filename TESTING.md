# Arizona ForeFlight Acceptance Test

Use the current `dist/freeman/Abandoned_Airports_AZ.zip`. If an earlier Arizona
pack was installed, delete it first so old hash-named waypoints do not remain.

## Import

1. Transfer the ZIP with AirDrop, Files, email, Finder, or a configured cloud
   document provider, and open it with ForeFlight.
2. Confirm the pack appears under **More > Custom Content > Content Packs** as
   **Historical Airfields - Arizona**, version 2.1.
3. Confirm ForeFlight reports 115 waypoints/documents and no import error.

## Map behavior

1. Enable **User Waypoints** on Maps.
2. Search for `AZ_AIR_TOPIA_AIRPORT`; confirm it appears near Phoenix at
   33.400, -112.160.
3. Search for these regional samples and confirm each opens at the expected
   location:

   - `AZ_KOCH_FIELD` — Flagstaff area, 35.270, -111.514
   - `AZ_MARSH_DOWNTOWN_AIRPORT` — Yuma, 32.710, -114.610
   - `AZ_ALLIED_AIRFIELD` — Tucson, 32.150, -110.850
   - `AZ_KINGMAN_AUXILIARY_AIRFIELD_1` — northwestern Arizona, 35.740, -114.090
   - `AZ_DOUGLAS_AUXILIARY_ARMY_AIRFIELD_2` — southeastern Arizona, 31.370, -109.670

4. Zoom out and pan statewide. Check that labels remain usable and do not
   overwhelm the map at normal planning zoom levels.
5. Add one waypoint to a route only to confirm ForeFlight recognizes it as a
   waypoint. Do not use the historical coordinates operationally.

## Attached histories

For at least one short document and one long document:

1. Tap the waypoint and open its attached airport-named PDF.
2. Confirm the title is readable and no random hash is shown in the UI.
3. Page through the entire PDF; check for blank pages, clipped text, rotated or
   missing images, and unreadable captions.
4. Confirm the informational-use notice and Paul Freeman attribution appear.
5. Turn on Airplane Mode and reopen the document to confirm images are offline.
6. Tap the source link once while online and confirm it opens the appropriate
   Airfields-Freeman regional page.

Suggested long-document test: `AZ_GILA_RIVER_MEMORIAL_AIRPORT_34AZ` (29 pages,
44 images in the current build).

## Update and removal

1. Close and reopen ForeFlight; confirm the pack and waypoints persist.
2. Delete the content pack and verify its waypoints disappear.
3. Reimport the same ZIP and confirm it does not create duplicate waypoints.
4. Record the ForeFlight version, iOS/iPadOS version, device, subscription tier,
   import method, and any screenshots of unexpected behavior.

## Pass criteria

- Exactly one marker and one attached PDF for every sampled airport.
- Human-readable waypoint and document names with no hash identifiers.
- Correct map positions and searchable IDs.
- Complete PDFs available offline.
- Clean delete/reimport behavior with no duplicates or import warnings.

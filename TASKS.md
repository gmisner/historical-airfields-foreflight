# Project tasks

## In progress

- [x] Bring every state package up to the Arizona 2.1 structure:
  - [x] readable, state-prefixed waypoint IDs
  - [x] descriptive state-specific KML layer name
  - [x] airport-style waypoint marker
  - [x] state-specific embedded README
  - [x] consistent manifest and validation
- [x] Generate airport-named rich PDF histories and cache authorized source
  images for the remaining states.
  - [x] Alabama
  - [x] Alaska
  - [x] Arkansas
  - [x] Arizona
  - [x] California
  - [x] Colorado
  - [x] Connecticut
  - [x] Delaware
  - [x] Florida
  - [x] Georgia
  - [x] Hawaii
  - [x] Idaho
  - [x] Illinois
  - [x] Indiana
  - [x] Iowa
  - [x] Kansas
  - [x] Kentucky
  - [x] Louisiana
  - [x] Maine
  - [x] Maryland
  - [x] Massachusetts
  - [x] Michigan
  - [x] Mississippi
  - [x] Minnesota
  - [x] Missouri
  - [x] Montana
  - [x] Nebraska
  - [x] Nevada
  - [x] New Hampshire
  - [x] New Jersey
  - [x] New Mexico
  - [x] New York
  - [x] North Carolina
  - [x] North Dakota
  - [x] Ohio
  - [x] Oklahoma
  - [x] Oregon
  - [x] Pennsylvania
  - [x] Rhode Island
  - [x] South Carolina
  - [x] South Dakota
  - [x] Tennessee
  - [x] Texas
  - [x] Utah
  - [x] Virginia
  - [x] Vermont
  - [x] Washington
  - [x] West Virginia
  - [x] Wisconsin
  - [x] Wyoming
  - [x] All 50 states complete
- [x] Visually inspect representative short and long histories from every
  state before publishing.

## Hosting

- [ ] Reauthenticate the GitHub CLI for the `gmisner` account.
- [ ] Create one public repository named `historical-airfields-foreflight`.
- [x] Keep scripts, documentation, and reviewed metadata in Git.
- [x] Exclude source-page caches, image caches, generated PDFs, ZIP packages,
  temporary renders, and other build artifacts from Git history.
- [ ] Publish finished state ZIPs as assets on versioned GitHub Releases.
- [x] Add direct ForeFlight installation links to the release notes and user
  documentation.

## Release gate

- [x] Validate every archive locally.
- [x] Confirm every waypoint has exactly one associated rich PDF.
- [x] Confirm no legacy `AA_<STATE>_...` identifiers remain.
- [ ] Test import, markers, offline histories, deletion, and reimport in
  ForeFlight for representative states.
- [x] Publish only completed states; mark partial batches as prereleases.

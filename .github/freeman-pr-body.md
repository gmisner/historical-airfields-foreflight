## Summary

Automated weekly scan of Paul Freeman's authorized source pages. This PR is draft-only and is created for human review; it does not build packs, merge changes, tag releases, or publish assets.

## Source

- https://www.airfields-freeman.com/
- `python scripts/fetch_freeman.py --all-states --refresh`

## Review requirements

- Distinguish additions, removals, and page reorganization from markup-only changes.
- Preserve reviewed editorial fields in `data/freeman_review.csv`.
- Retain any apparent removals until the owner confirms them.
- Rebuild and validate affected state packs only after the source changes are reviewed.
- Publish a release only after the owner explicitly authorizes that release.

## Safety

Historical packs are informational references only and are not for navigation, flight planning, landing decisions, or operational use.

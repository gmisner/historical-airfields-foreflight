# Publishing a release

The repository contains the reviewed metadata, builders, validation tools, and
documentation. Generated source caches, images, PDFs, and ZIP files remain out
of Git; the finished state ZIPs belong on a versioned GitHub Release.

## One-time repository setup

1. Restore GitHub CLI authentication:

   ```sh
   gh auth login -h github.com
   gh auth status -h github.com
   ```

2. Create the public repository `gmisner/historical-airfields-foreflight`, or
   rename the existing underscore-named repository to that name.

3. Point this checkout at the final repository URL:

   ```sh
   git remote set-url origin https://github.com/gmisner/historical-airfields-foreflight.git
   ```

4. Review the working tree carefully, then commit and push the source,
   metadata, and documentation. Do not add anything ignored by `.gitignore`.

## Prepare and publish version 2.1.0

First run the local release audit. It verifies all 50 archives, writes SHA-256
checksums, and regenerates `PACKS.md` with direct ZIP and ForeFlight links.

```sh
python3 scripts/prepare_release.py --tag v2.1.0
```

After checking `PACKS.md` and `dist/freeman/SHA256SUMS.txt`, publish the 50 ZIP
files and checksum file:

```sh
python3 scripts/prepare_release.py --tag v2.1.0 --publish
```

Finally, open several links from `PACKS.md` on an iPhone or iPad, import the
packs into ForeFlight, and complete the representative-state checks in
`TESTING.md`.

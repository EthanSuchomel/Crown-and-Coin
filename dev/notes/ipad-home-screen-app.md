# Crown & Coin — iPad home-screen app

- Play link: https://ethansuchomel.github.io/Crown-and-Coin/
- Hosted on GitHub Pages from the repo EthanSuchomel/Crown-and-Coin (branch main, root folder).
- Works offline and full screen once added to the iPad home screen (Safari → Share → Add to Home Screen).
- Online play vs another person still only works from the claude.ai link: https://claude.ai/artifact/7jbdEk6pGqUo5z36bGR7gj
- Updating: after changing the game, rebuild the site files (index.html, arena.html, sw.js with a new version, manifest, icons) and push to the repo. The iPad picks up the new version the next time the app is opened with WiFi on.

## The claude.ai link now runs the repo version (2026-11-09)
- Ethan's decision (2026-11-07, confirmed 2026-11-09): the claude.ai link carries the repo version. Done on 2026-11-09: version 1794284534-6f89 has the Mythical faction, the Dinosaur rework (volcano, Alamosaurus guards, new roster and art) and all arena work since Nov 6. Its online-play capabilities (db, room, user) were kept.
- The old link version's Nov 1 computer-player upgrade (arena-calibrated odds `ARENA_CAL`/`arenaRules`/`arenaO`/`SIM_ARENA`/`AI_PLANNING`, and an arena general that plays by difficulty) never reached the repo; it stays in the link's version history and can be rebuilt from computer-opponent-notes.md.
- **To update the link after a repo change:**
  1. `python3 dev/claude-version/make_claude_version.py index.html OUT.html` (drops the home-screen app lines: icons, manifest, standalone styles, the offline worker).
  2. Publish OUT.html to the link's URL, with `arena.html` and every file in `dino/` and `myth/` (skip the stray `myth/myth` symlink) under the same paths: about 37 MB. Don't pass capabilities (keeps db/room/user).
  3. The publish needs a session that can read and write that artifact (read `arena.html` first if the publish asks).

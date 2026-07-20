# AGENT_LOG — AutoStack

**Repo:** OneByJorah/AutoStack
**Pipeline:** Repo Polish (serial)
**Date:** 2026-07-20
**Agent:** opencode/big-pickle

---

## Intake Scan

| Check | Result |
|-------|--------|
| Fake capture-screenshots.py | NONE |
| Fake mockup PNGs | **5 IDENTICAL FAKE SCREENSHOTS** — all same file (MD5: 59b7e92108abe34a181c2aadd4acfbc8), 2095 bytes each, labeled as different services |
| README honesty | Title said "StackDeploy" (wrong repo), clone URL pointed to wrong repo |
| Clone URL | WRONG — pointed to `OneByJorah/StackDeploy` |
| Author credit | Present but format inconsistent |
| LICENSE | MIT — fixed copyright holder |
| docker-compose.yml | Valid — SearXNG, Qdrant, Honcho, Obsidian (caddy), Selenium |
| Overlay compose files | portainer.yml, headroom.yml, honcho.yml — all valid |
| .env.example | Header referenced old name "arah" |
| live-manifest.json | Referenced old name "arah" |

## Repo History

This repo was previously named "arah", then renamed to AutoStack. But the README still referenced "StackDeploy" (a third name), and internal files still referenced "arah".

## Fixes Applied

1. **Deleted 5 identical fake screenshots** (docs/screenshots/*.png) — all were the same 2095-byte placeholder renamed 5 times
2. **README.md** — Fixed title ("StackDeploy" → "AutoStack"), clone URL, project structure dir name, VCS reference, overview text, Hermes integration paths, author line (added "/ JorahOne LLC")
3. **README.md** — Replaced fake "live captures" screenshot section with honest "CLI/infrastructure stack. No screenshots available."
4. **LICENSE** — Added "/ JorahOne LLC" to copyright line
5. **live-manifest.json** — Fixed repo references (arah → AutoStack)
6. **FIXES.md** — Fixed title (arah → AutoStack)
7. **.env.example** — Fixed header (arah → AutoStack)
8. **docs/SERVER_SETUP.md** — Fixed clone URL and cd path
9. **docs/HERMES_SETUP.md** — Fixed clone URL and cd path

## Remaining "StackDeploy" refs (intentionally kept)

Internal tool names in noc-dashboard/, scripts/, backend code — these are functional identifiers, not user-facing repo references. Changing them could break runtime behavior.

## Verdict

**FIXED** — Removed fake screenshots, corrected repo identity across all user-facing files, fixed license.

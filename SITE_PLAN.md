# Plan — refresh the data reports and publish them as a website

*Drafted 2026-10-13.*

**Decisions so far**
- **Content on the site:** the four data reports — `romania/`, `greece/`, `it-romania/`, `china-industry/`. Not on the site (for now): `bolojan/`, `SAFE/`, `curs/`, `it-romania/BLOG.md`.
- **Generator:** MkDocs + Material theme (free, MIT; installed into the existing `.venv`). If Material is ever abandoned, Zensical reads the same `mkdocs.yml` and Markdown.
- **Hosting:** GitHub Pages from this repo (`mihaigociu/economie`, **already public**, confirmed 2026-10-13; Pages not yet enabled). Built by GitHub Actions, so it costs nothing.
- **Language:** English only.

---

## Phase 0 — Repo housekeeping

The repo is already public, so `SAFE/`, `bolojan/` and `curs/` are already readable on GitHub. Leaving them off the website is only about what the site presents.

- [ ] Keep `.claude/` out of git. It's untracked today (it holds local permissions and personal paths); add `.claude/` to `.gitignore` explicitly.
- [ ] Leave the untracked `it-romania/BLOG.*` files uncommitted, or move them out of the repo.
- [ ] Add a `LICENSE`: CC BY 4.0 for the text and charts, MIT for the scripts.

## Phase 1 — Bring the four reports up to date

### Common procedure for each report
1. Copy `raw-data/` to a scratch directory to keep the old version for comparison.
2. Re-run the scripts (`../.venv/bin/python 01_…py` …). Fix any broken API calls (Eurostat dataset codes do get renamed).
3. **Compare old and new CSVs.** List new data points (mostly 2025) and any revisions of more than 0.2 pp or 2 % to history already in the text.
4. Regenerate the charts, then check axes, labels and end-years.
5. **Check every figure in the text against the CSVs.** Generalise `it-romania/_verify.py` into a shared `tools/verify.py` and run it on all four reports.
6. Rewrite the passages whose numbers or conclusions changed. Keep the analysis and voice the same; don't rewrite for the sake of it.
7. Add a line under the title: *"Data updated October 2026 — latest observations: …"* and a short "What changed since the April 2026 edition" box.
8. Commit each report separately.

### Per report
| Report | What's new | Effort |
|---|---|---|
| **Romania** (2000–2024) | 2025 GDP, deficit and debt (the 2025 deficit gets an Oct-2026 revision), 2025 HICP, labour market, current account. Update the 9.3 % framing to the 2025 outcome, without repeating the Bolojan report. Extend the title range to 2025. | Medium |
| **Greece** (2000–2025) | Most series end in 2024. Add 2025 GDP, debt (the debt-ratio trajectory), tourism receipts, NPLs, unemployment. Check the "16 % below 2007 peak" figures. | Medium |
| **Romanian IT** (1990–2025) | 2025 ICT value added and services exports, Eurostat 2025 ICT-usage survey (DESI-type indicators), ICT employment, EPO 2025 patent filings. | Low–medium |
| **China industry** | CSVs were curated by hand, so the scripts can't refresh them; only `00_fetch_world_bank.py` runs automatically. Go through `raw-data/SOURCES.md` series by series: 2025 trade surplus, EV and battery output and exports, industrial robot installations (IFR, World Robotics Sept 2026), solar and wind additions, rare-earth export controls, semiconductors. Update chapters 1, 3–7, 9 and 11. | **High** |

### Order and timing
1. **China first.** Its sources don't depend on the EU release calendar, and it's the largest job.
2. **Romanian IT.**
3. **Romania and Greece** after Eurostat's **October EDP notification** of deficit and debt figures (around 21–22 Oct 2026; check the release calendar). That release revises the 2025 deficit and debt numbers both reports depend on.

## Phase 2 — Build the site

### Layout
```
mkdocs.yml                 # at repo root
site-src/
  index.md                 # home: who I am, what the site is, latest updates
  about.md                 # method & sources (short; data from Eurostat/WB/ECB/IMF…)
  reports/romania  -> ../../romania           # symlinks, so each report exists only once
  reports/greece   -> ../../greece
  reports/it-romania -> ../../it-romania
  reports/china    -> ../../china-industry
.github/workflows/pages.yml
```
- `docs_dir: site-src`. `exclude_docs` hides `*.py`, `plan.md`, `raw-data/` and `requirements.txt`, so only `report.md` and `charts/` are published.
- If symlinks cause trouble, fall back to a small `tools/build_site.py` that copies `report.md` and `charts/` into `site-src/` before building.
- Output goes to `site/` (gitignored).

### Content adjustments (light)
- Remove repo-specific notes such as *"Charts in `charts/`, raw data in `raw-data/`"*. Turn CSV mentions into links to the files on GitHub (`https://github.com/mihaigociu/economie/blob/main/<report>/raw-data/…`).
- Add front matter to each report: title, description, date, "data updated" date.
- Check that every chart reference uses `![…](charts/x.png)`. Add `loading=lazy`, since the reports have 40–65 images each.
- Keep each report on one page with the table of contents in the sidebar. Split into chapters only if the China page gets too slow.

### Theme config (Material)
- Light and dark mode, built-in search, `navigation.tabs`, `toc.follow`, `content.code.copy`.
- Markdown extensions: `tables`, `footnotes`, `admonition` (for the "What changed" boxes), `attr_list`, `md_in_html`.
- Plugins: `search`, plus `glightbox` to click a chart and see it full size.
- Pin versions in a `requirements-site.txt`.

### Deploy
- `.github/workflows/pages.yml`: on push to `main` it checks out the repo, sets up Python, runs `pip install -r requirements-site.txt` and `mkdocs build --strict`, then uploads the result with `actions/upload-pages-artifact` and publishes it with `actions/deploy-pages`.
- Repo settings: Pages → Source: *GitHub Actions* (the only manual step; the repo is already public).
- URL: `https://mihaigociu.github.io/economie/` (custom domain optional, later).
- Preview locally with `.venv/bin/mkdocs serve`.

### Done when
- [ ] `mkdocs build --strict` passes with no broken links or images.
- [ ] All four reports render on desktop and mobile, the charts open full size, and search finds report text.
- [ ] The workflow is green and the site is live at the Pages URL.
- [ ] Top-level `README.md` links to the site.

## Later (optional)
- Add `bolojan/` and `SAFE/` as dated "Notes" with postscripts on what happened after May 2026.
- Add `curs/` as a "Course" section once more lessons are written.
- RSS feed for new and updated articles, an Open Graph image per report, and a custom domain.

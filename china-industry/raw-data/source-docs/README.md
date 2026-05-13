# Source documents

This folder is for **freely-downloadable** primary source documents (PDFs,
data exports) that back the figures used in the charts. Each CSV in
`raw-data/` cites a source URL; where that source is a free downloadable
file, you can keep a copy here for a fully self-contained audit trail.

This is optional — every URL is also in the CSV headers and in
`../SOURCES.md` — so you can always go back to the live source.

## Currently in this folder

| File | Source | Used by |
|---|---|---|
| `ember_global_electricity_review_2024.pdf` | Ember — Global Electricity Review 2024 | 07a, 07b |

## To add manually

Several primary sources block direct `curl` downloads (CDN/anti-bot
checks). To add them, open the URL in a browser and save the PDF here:

| Suggested filename | URL |
|---|---|
| `iea_global_ev_outlook_2024.pdf` | <https://www.iea.org/reports/global-ev-outlook-2024> |
| `iea_global_ev_outlook_2025.pdf` | <https://www.iea.org/reports/global-ev-outlook-2025> |
| `iea_critical_minerals_outlook_2024.pdf` | <https://www.iea.org/reports/global-critical-minerals-outlook-2024> |
| `iea_electricity_2024.pdf` | <https://www.iea.org/reports/electricity-2024> |
| `iea_energy_and_ai_2025.pdf` | <https://www.iea.org/reports/energy-and-ai> |
| `irena_renewable_capacity_statistics_2024.pdf` | <https://www.irena.org/Publications/2024/Mar/Renewable-capacity-statistics-2024> |
| `stanford_ai_index_2024.pdf` | <https://aiindex.stanford.edu/report/> |
| `stanford_ai_index_2025.pdf` | <https://aiindex.stanford.edu/report/> |
| `wipo_genai_patent_landscape_2024.pdf` | <https://www.wipo.int/web/patent-landscape-reports/generative-artificial-intelligence> |
| `ifr_world_robotics_2024_press_release.pdf` | <https://ifr.org/ifr-press-releases/news/world-robotics-2024-report> |
| `nsf_se_indicators_2024.pdf` | <https://ncses.nsf.gov/pubs/nsb20241> |
| `iaea_pris_under_construction_2024.csv` | <https://pris.iaea.org/PRIS/WorldStatistics/UnderConstructionReactorsByCountry.aspx> (export) |
| `bnef_battery_price_2024_press_release.html` | <https://about.bnef.com/insights/clean-energy/lithium-ion-battery-pack-prices-see-largest-drop-since-2017-falling-to-115-per-kilowatt-hour/> |

These are all free / no-registration sources. They are not committed
because (a) they are large and (b) many of them block automated downloads
in this environment. The URLs above are stable; download whichever you
need for offline audit.

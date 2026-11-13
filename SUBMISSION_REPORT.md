# Final assessment report

Prepared and verified locally on **13 November 2026 (India time)**. Project: `Honeybee-Digital`. Repository: [BitsbyBhargav/HoneyBee-Digital](https://github.com/BitsbyBhargav/HoneyBee-Digital). The application is complete for a local demonstration. The required video remains a user submission action.

## What was implemented

- React/Vite dashboard with responsive Recharts city, category and source visualizations, live KPI cards, directory search/filter/pagination, source links, manual refresh, loading/empty/error states and visible OSM attribution.
- FastAPI with protected bulk imports, all three mandatory count endpoints, coherent dashboard data, health, summary and paginated listings.
- Real MySQL `listing_master` with required columns, indexes, nullable phone, extra provenance and a unique normalized business fingerprint.
- Reproducible OpenStreetMap/Overpass collector, cached raw responses and exact queries, cleaning, validation, deduplication, provenance hashes and an ODbL notice.
- Safe separate native MySQL instance because the existing root credentials failed and Docker was unavailable. Original MySQL80 service remains intact.
- Actual populated SQL export, exact restore verification, backend/browser tests, screenshots, README and a timed video guide.

## Complete submission folder structure

```text
Honeybee-Digital/
├── .gitattributes
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pytest.ini
├── README.md
├── DEMO_GUIDE.md
├── RECORD_NOW.md
├── SUBMISSION_REPORT.md
├── backend/
│   ├── __init__.py
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── schemas.py
│   └── tests/
│       ├── conftest.py
│       ├── test_api.py
│       └── test_collector.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── playwright.config.js
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── Charts.jsx
│   │   ├── Listings.jsx
│   │   └── styles.css
│   └── tests/
│       └── dashboard.spec.js
├── data/
│   ├── LICENCE.md
│   ├── collect.py
│   ├── import_data.py
│   ├── listings.json
│   ├── metadata.json
│   └── raw/
│       ├── bengaluru.json
│       ├── bengaluru.overpassql
│       ├── chennai.json
│       ├── chennai.overpassql
│       ├── hyderabad.json
│       ├── hyderabad.overpassql
│       ├── pune.json
│       └── pune.overpassql
├── database/
│   ├── schema.sql
│   ├── demo_queries.sql
│   └── honeybee_dump.sql
├── scripts/
│   ├── local_mysql.py
│   ├── demo_database.py
│   ├── database.py
│   ├── refresh_probe.py
│   ├── verify_live.py
│   └── verify_dump.py
└── docs/
    ├── dashboard-desktop.png
    ├── dashboard-mobile.png
    ├── live-verification.json
    └── dump-verification.json
```

Local-only files/folders excluded from Git and the archive: `.env` (generated credentials), `.local/` (persistent project MySQL data, logs and temporary test backups), `.venv/`, Python caches, `.pytest_cache/`, frontend `node_modules/`, `dist/` and browser test output. Local `.git/` metadata is not part of the source archive.

## Requirement status

| Requirement | Status / evidence |
|---|---|
| React frontend | Complete; live dashboard, production build passed |
| FastAPI backend | Complete; OpenAPI at `/docs` |
| Mandatory MySQL | Complete; separate native MySQL 8.0 instance on loopback port 3307 |
| At least 500 listings | 9,109 real sourced POIs loaded and verified |
| Name/category/city/address/optional phone/source | Present and validated |
| Reproducible collection | Raw snapshots, exact Overpass queries, collector, metadata hashes |
| Honest methodology/licensing | API collection disclosed; OSM/ODbL attribution in dataset, README and UI |
| Required listing_master columns | Complete; generated schema and populated export |
| Bulk insert API | Complete; API key, validation, per-batch transaction, duplicate protection |
| City/category/source count APIs | Complete; all reconcile exactly to MySQL and dataset |
| Required dashboard charts | Complete; genuine source-wise count has one source |
| Response to database changes | Verified in Chromium with a real temporary row removal/restoration |
| Responsive/error/loading/empty states | Tested; desktop/mobile images visually inspected |
| Real SQL export and restore | 9,109 rows; exact match across every column |
| Backend automated tests | 18 passed on disposable real MySQL database |
| Browser tests | 5 passed on Chromium; desktop and 390px mobile |
| Docker Compose configuration | Provided with loopback port and persistent volume; not executed |
| GitHub preparation | Published repository; credentials and local runtime files excluded |
| README and demo outline | Complete |
| Video recording | User action; not recorded |
| GitHub publication | Published to `BitsbyBhargav/HoneyBee-Digital` on `main` |

## Actual dataset and provenance

Source: **OpenStreetMap contributors through the Overpass API**. This is a structured community POI source, not Google Maps/Justdial scraping and not a comprehensive verified commercial directory. Data licence: [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); [attribution](https://www.openstreetmap.org/copyright).

| Metric | Result |
|---|---:|
| Source objects returned | 9,152 |
| Exact normalized duplicates removed | 43 |
| Final records in dataset and MySQL | **9,109** |
| Bengaluru | 4,649 |
| Chennai | 1,345 |
| Hyderabad | 1,331 |
| Pune | 1,784 |
| Distinct categories | 174 |
| Distinct sources | 1 |
| Records with supplied phone strings | 2,525 |
| Synthetic records in dataset | 0 |

Snapshot times and SHA-256 hashes are in `data/metadata.json`. Phone values, actual operation and municipality membership were not independently verified. Some addresses are street-only and category tags are broad. City assignment can use an approximate query scope when no recognized city tag is present. Exact matching does not eliminate fuzzy duplicates. These limitations are documented rather than hidden.

## Execution and test results

1. Connected to the separate project MySQL and created `listing_master`.
2. Imported 9,109 rows using the API; reimport inserted zero and skipped all 9,109 duplicates.
3. Verified every dataset fingerprint against MySQL, and all city/category/source group counts against the dataset and API.
4. Ran 18 passing backend tests with synthetic fixtures only in a generated test database.
5. Ran 5 passing browser tests, including real FastAPI responses and a real database update/refetch sequence. Restored the backed-up row, ID and timestamp after the check.
6. Built frontend production assets successfully with separate chart bundle; npm audit reported zero known vulnerabilities at installation time.
7. Produced a native mysqldump export and restored it into a separate generated MySQL database. All 9,109 rows and all columns matched exactly; temporary restore database was removed.
8. Rendered and inspected desktop and mobile screenshots.

Pytest reports one upstream Starlette/httpx deprecation warning; it does not fail the tests. Not tested: Docker, existing-service password reset, other browser engines, production hosting, high-load/concurrent import performance. A transient Overpass 504 occurred during initial collection; the final four-city snapshot succeeded. There are no blocked mandatory local implementation requirements. A reviewer requiring literal HTML scraping should be told this submission uses the permitted structured-source alternative.

## Exact run and database commands

Full first-time setup, Docker option and environment configuration: [README](README.md#windows-quick-start).

Terminal 1:

```powershell
cd 'C:\Users\offic\OneDrive\Desktop\Assesment\Honeybee-Digital'
.\.venv\Scripts\python.exe scripts\local_mysql.py start
.\.venv\Scripts\python.exe scripts\database.py setup
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
cd 'C:\Users\offic\OneDrive\Desktop\Assesment\Honeybee-Digital'
.\.venv\Scripts\python.exe data\import_data.py
cd frontend
npm.cmd run dev
```

Dashboard: `http://127.0.0.1:5173`. API docs: `http://127.0.0.1:8000/docs`.

Export/check restore, from the project root:

```powershell
.\.venv\Scripts\python.exe scripts\database.py export
.\.venv\Scripts\python.exe scripts\verify_dump.py
```

Manual restore to a new database:

```powershell
.\.venv\Scripts\python.exe scripts\database.py restore --database honeybee_restored
```

The original MySQL80 service on port 3306 is independent. The native helper generates its own credentials and persistent data, and checks instance ownership before stopping the project server. It never resets/deletes original databases.

## GitHub and recording instructions

Repository: [BitsbyBhargav/HoneyBee-Digital](https://github.com/BitsbyBhargav/HoneyBee-Digital). To publish future changes from the project root:

```powershell
git status
git check-ignore .env .local .venv frontend/node_modules
git add .
git commit -m "Describe your changes"
git push origin main
```

The repository contains code, data, tests, the populated SQL dump and documentation, with credentials/runtime files excluded. Preserve data attribution when sharing it. Publishing source code does not host the website: reviewers must use the README to run it locally. Follow [DEMO_GUIDE.md](DEMO_GUIDE.md) to record the 4-minute-20-second outline. It specifies commands, screens, narration and technical points; the recording itself remains your task.

## Final submission checklist

- [x] Required technology stack and all required APIs implemented.
- [x] At least 500 sourced records loaded; actual count and limitations disclosed.
- [x] React connected to FastAPI/MySQL; meaningful tests and build passed.
- [x] SQL schema and genuine populated dump included and restore-tested.
- [x] README, source licence/provenance and demonstration guide included.
- [x] Credentials and local runtime directories excluded from source submission.
- [ ] Review the code and explain each component in your own words.
- [x] Commit/push to the public `BitsbyBhargav/HoneyBee-Digital` repository.
- [ ] Record a 3–5 minute demonstration and confirm its sharing permissions.
- [ ] Submit the repository URL, video link and populated SQL export as requested by the company.

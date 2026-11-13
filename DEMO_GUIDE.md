# Demonstration recording guide (target: 4 minutes 20 seconds)

For an immediate recording, use [RECORD_NOW.md](RECORD_NOW.md), which includes exact narration and a read-only command to show the live MySQL table directly in VS Code: `.\.venv\Scripts\python.exe scripts\demo_database.py`.

Record your screen and your own narration. This file is an outline; **no video has been recorded**. Show source code and working outputs you can explain. Keep `.env` and administrative credentials out of the recording; show `.env.example` when discussing configuration.

## Before recording

Open the project in VS Code. Have browser tabs ready for `http://127.0.0.1:5173` and `http://127.0.0.1:8000/docs`. Increase terminal/browser text size if necessary. Close unrelated personal tabs and notifications.

Terminal 1, from the project root:

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
.\.venv\Scripts\python.exe scripts\verify_live.py
cd frontend
npm.cmd run dev
```

Terminal 3, for short recorded commands:

```powershell
cd 'C:\Users\offic\OneDrive\Desktop\Assesment\Honeybee-Digital'
```

The configured database should contain 9,109 rows. The existing import reports duplicates; this is expected. Avoid `--refresh` during recording: the shared Overpass service can be slow and new data can change the snapshot. The default collector processes cached raw data without making new requests, which you should explain accurately.

## Timed outline and natural narration

| Time | Exact screen / action | Suggested narration |
|---|---|---|
| 0:00–0:25 | Dashboard with KPI cards and charts; VS Code folder tree briefly | “This is my Business Listings Dashboard for the Honey Bee Digital assessment. React reads a FastAPI backend, and the records and aggregate queries use MySQL. The current dataset has 9,109 sourced listings across four collection areas.” |
| 0:25–1:10 | `data/collect.py`, one `.overpassql` file, one raw JSON object, then `data/metadata.json` | “I collected structured OpenStreetMap points of interest using the Overpass API. This is API collection, not HTML scraping from Google Maps. Queries select named shops and selected services with supplied street or full addresses. I keep the original objects, exact queries, source links and file hashes. I normalize text, map recognized city aliases and remove exact duplicates. I do not invent missing phone numbers or addresses.” |
| 1:10–1:25 | Terminal 3: run `.\.venv\Scripts\python.exe data\collect.py` | “This run uses the saved responses and reproduces the cleaned dataset without network requests. Live recollection is available separately. OSM data is community maintained under ODbL, so addresses, category tags and contacts may be incomplete.” |
| 1:25–1:55 | `database/schema.sql`, `.env.example`, `scripts/local_mysql.py` overview | “The table is listing_master. It has the required fields, a primary key, grouping indexes, optional phone values and a unique fingerprint based on name, city and address. My original local root account was inaccessible, so this project runs a separate MySQL instance on port 3307 and keeps its credentials out of Git. It does not modify my existing service.” |
| 1:55–2:40 | Swagger: execute GET health, GET city/category/source endpoints; show POST bulk schema. Terminal: run `.\.venv\Scripts\python.exe data\import_data.py` | “These are the required aggregate APIs. They group rows in MySQL and return structured counts. Bulk insert requires an API key, validates records with Pydantic and uses a transaction per batch. This repeat import reports zero inserts and 9,109 duplicates, demonstrating that imports do not inflate the dashboard.” |
| 2:40–3:30 | Dashboard: city bars, category bars, source ring, values details; search, filter city, clear filters, next page, Refresh | “Every number here comes from the backend. The category chart shows the largest six plus the combined remainder; the full category values are available. There is one actual source, OpenStreetMap. Search, filters and pagination operate on directory records, while the charts show overall totals. Refresh requests the latest database snapshot.” |
| 3:30–3:50 | Browser narrow/mobile width; show table scrolling; restore desktop | “The cards and charts adapt to a mobile viewport. The wide directory scrolls inside its own panel. Loading, empty results and connection errors have explicit states.” |
| 3:50–4:20 | `docs/live-verification.json`, `docs/dump-verification.json`, test output if already available; `database/honeybee_dump.sql` and README | “I verified all three grouped totals against the dataset and MySQL. Eighteen backend tests and five browser tests pass. The browser suite also checks that a real database change appears after Refresh and restores the original row. This is a populated SQL export, and its restore matched every column. The README includes setup and reproducibility instructions. This is a local assessment, not a production deployment.” |

## Optional preparation evidence

Run these before recording so results are ready to show without waiting:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts\verify_live.py
.\.venv\Scripts\python.exe scripts\database.py export
.\.venv\Scripts\python.exe scripts\verify_dump.py
cd frontend
npm.cmd run test:e2e
npm.cmd run build
```

The browser suite briefly removes and restores one backed-up project row. Let it finish before recording. If interrupted, run `scripts/refresh_probe.py restore` as described in the README. Do not rerun data collection/import/export in parallel with that probe.

## Be ready to explain

- Why React talks to FastAPI rather than MySQL directly.
- How a SQL GROUP BY produces a chart dataset, and why its sum matches total rows.
- Why phone is nullable text rather than an integer.
- Why one source means a single 100% source segment.
- How the fingerprint and database unique constraint prevent repeat-import duplicates; why fuzzy duplicates can remain.
- Why missing contacts and street-only addresses are retained transparently.
- Why query scope is not an independently verified city boundary.
- Why OSM attribution/share-alike applies to the data and dump.
- Why the local import key stays on the backend and is absent from React.
- Why MySQL setup is explicit, sessions are request-scoped, and bulk batches are transactional.

## Final recording checks

- Keep the result between 3 and 5 minutes.
- Confirm text and chart values are legible and your microphone is clear.
- Verify the video shows data collection methodology, API execution and working UI controls.
- Do not call API collection HTML scraping, claim verified phone accuracy, or claim Docker was tested.
- Upload/share the recording yourself according to the company's submission instructions, and test its access permissions.

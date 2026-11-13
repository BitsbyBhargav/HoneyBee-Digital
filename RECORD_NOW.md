# Record now — complete assessment demo in about 4 minutes 45 seconds

Use **MySQL**, not Microsoft SQL Server (MS SQL). They are different products. The required MySQL database already exists: `honeybee`, table `listing_master`, with 9,109 rows at verification. You can demonstrate it directly in VS Code; MySQL Workbench is optional.

## Prepare these screens

1. VS Code with the `Honeybee-Digital` folder open and a PowerShell terminal at the project root.
2. Dashboard: http://127.0.0.1:5173
3. API documentation: http://127.0.0.1:8000/docs
4. GitHub: https://github.com/BitsbyBhargav/HoneyBee-Digital

Keep `.env` closed throughout the recording. `.env.example` is safe to show. Increase text size so terminal results are legible. Use the existing running servers if both URLs work.

For the commands during recording, first set this terminal's working directory:

```powershell
cd 'C:\Users\offic\OneDrive\Desktop\Assesment\Honeybee-Digital'
```

If the servers have stopped, use separate terminals before recording:

```powershell
# Terminal 1, project root: MySQL then FastAPI. Leave FastAPI running.
.\.venv\Scripts\python.exe scripts\local_mysql.py start
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

```powershell
# Terminal 2: React. Leave it running.
cd 'C:\Users\offic\OneDrive\Desktop\Assesment\Honeybee-Digital\frontend'
npm.cmd run dev
```

Do not start second copies if those ports are already serving the app. The database is already populated, so there is no need to recreate it. Have a third terminal at the root for the demonstration commands below.

## 0:00–0:20 — Introduction

**Screen:** Dashboard, showing the total and charts.

**Say:**

“Hello, I’m Bhargav. This is the Business Listings Dashboard for the Honey Bee Digital internship assessment. It uses React for the interface, FastAPI for the backend, and MySQL for persistence. The current dataset contains 9,109 sourced listings across four collection areas.”

## 0:20–1:05 — Collection and data flow

**Screen:** Open `data/collect.py`. Point to `CITIES`, `query_for()` and `listing_from_element()`. Then open `data/metadata.json` and show the count, duplicate exclusions and source details.

**Say:**

“I used OpenStreetMap points of interest through the Overpass API. This is structured API collection. The collector selects named shops and selected services with supplied street or full addresses. It normalizes text, maps recognized city aliases, preserves source addresses and leaves missing phones empty. It removes exact duplicates using a fingerprint based on name, city and address. Raw snapshots, queries and hashes make the process traceable. The final dataset has 9,109 records after removing 43 duplicates.”

“The flow is collection, validation, a protected import API, MySQL storage, FastAPI queries, and React charts.”

**Important:** Default collector execution rebuilds from cached responses; `--refresh` requests new data. Explain that if asked. Avoid a live external fetch during this timed recording.

## 1:05–1:45 — Show the real MySQL table

**Screen:** Run this in the root terminal:

```powershell
.\.venv\Scripts\python.exe scripts\demo_database.py
```

Show the database name and SHOW TABLES result. Scroll through columns, the total count, sample rows and grouped city counts. The command is read-only and prints no credentials.

**Say:**

“This output comes directly from our running MySQL server. The database is honeybee and the table is listing_master. It contains the required business fields, an auto-increment primary key and creation timestamp. Phone is nullable text. A unique fingerprint prevents repeated imports from adding the same identity again. City, category and source have indexes. The actual stored count is 9,109.”

If you prefer a graphical MySQL client, `database/demo_queries.sql` contains the same queries. The terminal output is sufficient evidence of the table; MS SQL is not needed.

## 1:45–2:45 — Demonstrate the APIs and duplicate-safe import

**Screen:** In Swagger, expand each of these, click **Try it out → Execute**, and show its 200 response:

- `GET /api/health`
- `GET /api/analytics/cities`
- `GET /api/analytics/categories`
- `GET /api/analytics/sources`

**Say:**

“The health endpoint checks both the connection and table readiness. These three required analytics endpoints group and count records inside MySQL. The city totals reconcile to 9,109. There is one actual source, OpenStreetMap, so the source response correctly contains one group.”

**Screen:** Briefly show `POST /api/listings/bulk` in Swagger, then run the importer from the terminal. Do not type/show the real import key on camera.

```powershell
.\.venv\Scripts\python.exe data\import_data.py
```

Expected on the already populated database: received 9,109; inserted 0; duplicates 9,109.

**Say:**

“Bulk insertion requires a server-side API key and validates incoming records with Pydantic. The importer sends batches of 500. This repeated import inserts zero additional rows, so it does not inflate the dashboard. Each batch has its own transaction.”

## 2:45–3:45 — Demonstrate React functionality

**Screen/action sequence:**

1. Return to the dashboard and point to city, category and source charts.
2. Open the category chart's values list if time allows.
3. Scroll to the directory and search for `1311`.
4. Clear filters, choose Pune, then clear again.
5. Click Next page, then Refresh data.
6. Briefly narrow the window to show the mobile arrangement.

**Say:**

“React fetches real JSON from FastAPI. These cards and charts use database results. The category chart displays the largest six groups plus the combined remainder, while the full values remain available. The directory supports server-side business-name search, city and category filters, and pagination. Directory filters do not change the overall charts. Refresh refetches the current database snapshot. The layout adapts to a narrow screen, and the directory table scrolls within its panel.”

Do not claim automatic source synchronization or a continuously streaming dashboard. Refresh rereads MySQL; it does not recollect OpenStreetMap.

## 3:45–4:15 — Testing and real export

**Screen:** Open `docs/live-verification.json`, `docs/dump-verification.json` and the `database/honeybee_dump.sql` filename. Show the reports' counts and exact_match field; avoid scrolling through thousands of SQL record values.

**Say:**

“The verification checks match the dataset identities and all grouped counts with MySQL and the API. Eighteen backend tests and five Chromium browser tests passed during implementation. The browser tests include a real database change followed by refresh, then restoration of the original row. This populated SQL dump was restored into a separate database, and all 9,109 rows matched across every column.”

These statements refer to executed implementation checks. The reports are saved evidence, not a claim that tests are running on screen now. If you want fresh short output prepared before recording, run `.\.venv\Scripts\python.exe -m pytest`. Do not run the browser database-change test concurrently with the video/import/export.

## 4:15–4:45 — Limitations and submission

**Screen:** GitHub repository and README setup instructions.

**Say:**

“The README explains Windows setup, environment configuration, collection, testing and SQL export. The dataset is attributed to OpenStreetMap under ODbL. Community data can be incomplete or outdated; phone numbers and present business operation were not independently verified, and city scopes are approximate. This submission runs locally. Reviewers can clone the repository and follow the README to start it. The source, populated SQL dump and this demonstration form the submission. Thank you.”

## Submit immediately after recording

- Repository: https://github.com/BitsbyBhargav/HoneyBee-Digital
- Video: your recorded 3–5 minute demonstration; confirm the reviewer can access it.
- Database export: `database/honeybee_dump.sql` in the repository, or attach it if the company requests a separate file.
- Optional source ZIP: use the updated `Honeybee-Digital-submission.zip`; it excludes credentials and local runtime data.

Follow the company's submission form/email instructions. Do not submit the localhost URL as a public website link: it works only on the computer running the servers. No public deployment or recorded video is claimed by the repository.

# ERP Sales Dashboard with AI

## About me
I'm Yaseen, a Business Informatics student. This is a one week CV project. I must be able to explain every table and every line of code in an interview.

## How to reply
* Start every reply with Hey Yaseen.
* Keep replies short, with a simple, easy to follow structure.
* Before writing code, explain in plain English what it will do and why.
* Go one step at a time. When I need to run something, give the exact command and say where to run it (PowerShell, Supabase SQL Editor or the browser).
* Explain every change in plain English.

## Rules
* Synthetic data only. Never real or private data.
* Never put API keys, passwords or database credentials in code or in the repo. Use a .env file locally (it is already in .gitignore) and Streamlit secrets when deployed.
* Keep code short with clear names. Put a plain English comment above each table and each function.
* Don't add anything I haven't asked for.
* AI question box: use Claude Haiku first. Connect through a read only database role that can only see the views. Accept a single SELECT query only, with a row limit, a timeout and a daily limit on AI questions. Keep preset questions as a fallback.

## Setup
* Repo: C:\Users\yassi\projects\erp-dashboard on Windows (I use PowerShell). GitHub: Yaseen-ElGendy/erp-dashboard.
* Database: PostgreSQL on Supabase. The Data API is off, so Python connects directly with the connection string stored in .env.
* I run SQL myself in the Supabase SQL Editor and keep the SQL files in the repo.
* Stack: Python, Streamlit, Claude API.

## Tables
customers, vendors, products, sales_orders, order_lines, stock_levels. See schema.sql.

## Plan (finish by Saturday 21 November 2026)
1. Data model: schema.sql (done, the six tables exist in Supabase and are empty). Next is seed.py, which generates about 12 months of synthetic data. Output: row counts I can state.
2. KPI views: views.sql with five views (monthly revenue, top products, order status, low stock, gross margin), each checked against a hand written query.
3. Dashboard: Streamlit app with KPI cards, three charts, and date and product filters.
4. AI question box: send the question and the table descriptions to the Claude API, get SQL back, run it, show the result and the SQL. Output: ten questions answered correctly.
5. Guardrails and tests: block anything that is not a read only query, add a row limit and a timeout, and try to break it with bad questions.
6. Deploy to Streamlit Community Cloud with secrets, then write the README with screenshots and an architecture sketch.
7. Finish: fix rough edges and pin the repo.

Stretch, only if ahead: next month revenue forecast, CSV export, a test file with 15 to 20 example questions.

I'm behind schedule (Day 1 started on Wednesday 18 November). If time runs short, drop the stretch items first, then shorten step 5. Never cut the AI question box or the deployment.

## README
Include a short How I built this section saying which parts I designed and which an AI tool wrote.

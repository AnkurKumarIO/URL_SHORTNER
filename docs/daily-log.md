# Daily Log — URL Shortener Project

## Day 1 — Understand & Plan
- **Built/Planned:** Architecture layout & short code strategy. Chose Option A (Random Base62 strings) to avoid sequential guessing/scraping.
- **Learned:** How database `UNIQUE` constraints handle race conditions without needing artificial delays or queues.
- **Open question:** How fast is Redis caching compared to PostgreSQL queries when someone clicks a link?
- **Prompt Log:** Prompted mentor on short code generation strategy (Option A vs B) and race condition handling.

So We choosed Option A as it protects our links from predictability and scraping.
And to handle the race condition we used database unique constrains i.e. 
In PostgreSQL, we mark the short_code column with a UNIQUE constraint.

Request #1 attempts to insert aB9x2K $\rightarrow$ Postgres saves it successfully.

Request #2 attempts to insert aB9x2K at the exact same millisecond $\rightarrow$ Postgres's engine detects the duplicate and instantly rejects the insert with a UniqueViolation error.

Our FastAPI backend catches that error, generates a new random short code (e.g. k9P3mL), and retries the insert seamlessly!
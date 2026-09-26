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


## Day 2 — Build the Memory
- **Built/Planned:** PostgreSQL database schema (`links` & `clicks` tables) and Redis caching layer (`cache.py`).
- **Learned:** 
  1. Why Foreign Keys (`link_id`) and `ondelete="CASCADE"` maintain database integrity when parent links are deleted.
  2. How a 24-hour Redis TTL balances high cache hit rates for viral traffic with strict memory control.
- **Open Question:** How will FastAPI handle reading from Redis first and falling back to PostgreSQL on a cache miss?
- **Prompt Log:** Justified the 24-hour Redis TTL strategy for burst traffic and defined `links` vs `clicks` table normalization.

We chose Option 2 (24-Hour TTL) for Redis because it prioritizes high-demand links—like when an event pass goes live and millions of people start clicking the same link on the same day. Storing links in Redis for 24 hours keeps popular links super fast in RAM when they are needed most, while automatically clearing out old, unused links after a day so our server memory doesn't overflow.

Links vs Clicks Table Distinction - 
We separated links and clicks into two distinct tables because a single link can be clicked thousands or millions of times (a One-to-Many relationship). Keeping them separate ensures that our main link lookup table stays small, clean, and fast, while every click event gets recorded as its own lightweight row without duplicating long URLs or locking the main table.

Foreign Keys & ondelete="CASCADE" -
link_id in the clicks table acts as a Foreign Key pointing back to id in the links table, making sure clicks can only be saved for real, existing links. Setting ondelete="CASCADE" means if a shortened link is ever deleted, PostgreSQL automatically deletes all its associated click history in one clean operation, leaving no leftover "orphan" data.
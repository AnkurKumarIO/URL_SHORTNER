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

## Day 3 — Build the Doorway
- **Built/Planned:** `POST /shorten` and `GET /r/{short_code}` endpoints in FastAPI with HTTP 307 temporary redirects and Redis cache-aside fallback.
- **Learned:** 
  1. Why HTTP 301 breaks click analytics (browsers cache redirects locally) while HTTP 307 forces browsers to contact our server on every click.
  2. How the Cache-Aside pattern works: Redis miss $\rightarrow$ PostgreSQL lookup $\rightarrow$ populate Redis cache $\rightarrow$ return redirect.
- **Open Question:** How will we record clicks in the background without slowing down the visitor's redirect speed?
- **Prompt Log:** Justified choosing HTTP 307 over 301 for analytics tracking and verified `redirect.py` cache execution flow.

### My Notes & Explanations:
- **Why HTTP 307 over 301:** I preferred Option B (HTTP 307) for this project because our aim is to record how frequently links are used and from where. It is better that every request is redirected by our server every time instead of getting saved in the browser's local cache.
- **First Click vs Second Click Execution:** When a user clicks a link for the first time, it is checked in the Redis cache first. If not found, it is queried from PostgreSQL, written back into Redis cache, and returned as a 307 redirect. When any user clicks the same link 5 seconds later, it is already present in the Redis cache, which is accessed immediately and returned at RAM speed.

## Day 4 — Build the Diary (Async Click Analytics)
- **Built/Planned:** Asynchronous click logging using FastAPI `BackgroundTasks` and analytics reporting endpoints (`GET /analytics/{short_code}` and `GET /analytics`).
- **Learned:** 
  1. Why blocking database writes slow down redirects under heavy traffic.
  2. How `BackgroundTasks.add_task()` decouples HTTP response delivery from disk I/O operations.
- **Open Question:** How will we connect our React frontend dashboard to display real-time click metrics and test app stability under chaos?
- **Prompt Log:** Justified Option B (async background tasks) over blocking writes for high-concurrency redirect performance.

### My Notes & Explanations:
- **Sync vs Async Decision:** I preferred Option B (Asynchronous Background Task) because we cannot make the user wait a long time, especially during heavy traffic bursts. Running click recording in the background keeps redirects fast.
- **BackgroundTasks Mechanism:** `background_tasks.add_task()` pushes the click logging job (short code, timestamp, referrer, user agent) into a background task queue. It does NOT wait for PostgreSQL to finish writing to disk before returning the HTTP 307 redirect response back to the user.
# ⚡ High-Performance URL Shortener Microservice

> A resilient, full-stack URL shortener built with **FastAPI**, **PostgreSQL**, **Redis**, and **React**. Designed for low-latency redirections (~1ms), non-blocking asynchronous click analytics, and automatic fault tolerance.

---

## 🌟 Key Features

* **⚡ Ultra-Low Redirection Latency (~1ms):** Uses **Redis Cache-Aside** strategy with a 24-hour TTL to serve viral links directly from memory.
* **🔒 Collision-Resistant Base62 Engine:** Generates random 6-character short codes ($62^6 = 56.8 \text{ Billion combinations}$) using CSPRNG (`secrets`). Handles database collisions atomically via PostgreSQL `UNIQUE` constraints and a retry loop.
* **📊 Decoupled Asynchronous Analytics:** Logs visitor details (click timestamps, HTTP referrers) in the background using FastAPI `BackgroundTasks` without delaying the HTTP 307 redirect response.
* **🛡️ HTTP 307 Redirect Protocol:** Uses HTTP 307 to prevent browsers from caching redirects locally, ensuring 100% accurate click tracking.
* **🌀 Chaos Resilient (Graceful Degradation):** Automatically degrades to PostgreSQL lookups if Redis crashes, ensuring zero downtime (HTTP 500 prevention).
* **⚛️ Single-Page React Analytics Dashboard:** Real-time dashboard built with React & Vite for generating links and tracking click metrics.

---

## 🏛️ System Architecture

```mermaid
graph TD
    subgraph Client_Layer ["Client Layer"]
        UserBrowser["🌐 User Web Browser"]
        ReactApp["⚛️ React Dashboard (Vite SPA)"]
    end

    subgraph Backend_Layer ["FastAPI Backend (ASGI)"]
        CORS["🛡️ CORS Middleware"]
        FastAPI["⚡ FastAPI Engine"]
        
        subgraph Routers ["API Routers"]
            ShortenRouter["📝 POST /shorten"]
            RedirectRouter["🔀 GET /r/{short_code}"]
            AnalyticsRouter["📊 GET /analytics"]
        end

        BackgroundTaskQueue["🧵 FastAPI BackgroundTasks (Async)"]
    end

    subgraph Storage_Layer ["Data & Caching Layer"]
        RedisCache[("⚡ Redis Cache (RAM)\nTTL: 24 Hours")]
        PostgresDB[("🐘 PostgreSQL DB\nTables: links, clicks")]
    end

    UserBrowser -->|HTTP 307 Redirect| RedirectRouter
    ReactApp -->|HTTP REST JSON| CORS
    CORS --> FastAPI
    FastAPI --> ShortenRouter
    FastAPI --> RedirectRouter
    FastAPI --> AnalyticsRouter

    ShortenRouter -->|1. Generate Base62| Base62Gen["🎲 Base62 Generator"]
    ShortenRouter -->|2. Save Link| PostgresDB
    ShortenRouter -->|3. Warm Cache| RedisCache

    RedirectRouter -->|1. Async Task Push| BackgroundTaskQueue
    RedirectRouter -->|2. Check Cache (1ms)| RedisCache
    RedirectRouter -.->|3. Fallback on Miss| PostgresDB

    BackgroundTaskQueue -->|4. Non-blocking Log| PostgresDB
    AnalyticsRouter -->|SQL Count Aggregation| PostgresDB
```

---

## 🛠️ Tech Stack

| Layer | Technology | Reason for Choice |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** (Python 3.11+) | Async ASGI speed (`uvloop`), Pydantic v2 validation, automatic OpenAPI specs. |
| **Database** | **PostgreSQL** | Enterprise ACID compliance, foreign key cascades (`ondelete="CASCADE"`), and B-Tree indexing. |
| **Cache Layer** | **Redis** | In-memory key-value store for ~1ms lookups with 24-hour TTL eviction. |
| **ORM** | **SQLAlchemy 2.0** | Type-safe query building and session dependency injection (`get_db`). |
| **Frontend** | **React 18 + Vite** | Lightweight SPA dashboard with real-time fetch metrics. |

---

## 📡 API Endpoints

| Method | Endpoint | Description | Sample Request / Response |
| :--- | :--- | :--- | :--- |
| `POST` | `/shorten` | Creates a shortened URL code. | **Body:** `{"url": "https://example.com"}`<br>**Response:** `{"short_code": "aB9x2K", "short_url": "http://localhost:8000/r/aB9x2K"}` |
| `GET` | `/r/{short_code}` | Redirects visitor to target URL. | **Status:** `HTTP 307 Temporary Redirect`<br>**Header:** `Location: https://example.com` |
| `GET` | `/analytics/{short_code}` | Returns metrics for a specific link. | **Response:** `{"short_code": "aB9x2K", "total_clicks": 42, "recent_clicks": [...]}` |
| `GET` | `/analytics` | Summarizes all shortened links. | **Response:** `[{"short_code": "aB9x2K", "total_clicks": 42}, ...]` |

---

## 🚀 Quickstart & Setup Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- Redis Server (or Docker Redis)
- PostgreSQL Server (or Docker Postgres)

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment & activate
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Redis & Postgres (if using local environment variables)
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/urlshortener"
export REDIS_URL="redis://localhost:6379/0"

# Run FastAPI dev server
uvicorn app.main:app --reload --port 8000
```
> The API interactive docs will be available at **`http://localhost:8000/docs`**.

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run Vite dev server
npm run dev
```
> Open **`http://localhost:5173`** in your browser to view the Analytics Dashboard.

---

## 🧪 Chaos Testing & Resiliency

To test system resilience against database and cache failures:
1. **Redis Failure Test:** Stop your local Redis service while the backend is running.
   - *Result:* `cache.py` catches the exception silently, degrades gracefully to PostgreSQL lookups, and continues delivering HTTP 307 redirects without throwing 500 errors.
2. **Postgres Fallback Test:** Unset `DATABASE_URL`.
   - *Result:* `database.py` automatically falls back to an embedded SQLite database (`urlshortener.db`) for seamless local development.

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

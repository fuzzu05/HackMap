# HackMap Data Pipeline & Recommendation Engine (Noor - Track 2 & Track 4)

This service is the production-grade Python data backend for HackMap, responsible for:
1. **Scraping Hackathons (Phase 2)**: Scrapy-based crawlers targeting global platforms (Devpost, MLH, Luma, Unstop).
2. **Data Normalization & Deduplication (Phase 1 & 2)**: Standardizing dates to UTC ISO-8601, normalizing currencies and tags, and deduplicating cross-listed hackathons via `DeduplicationEngine` (fuzzy title matching & SHA-256 similarity hashing).
3. **Ingestion Automation & Firestore Integration (Phase 3)**: Celery scheduled cron jobs (`beat_schedule` every 12 hours) upserting deduplicated records into `/hackathons` in Firestore.
4. **Personalization Engine (Phase 4)**: Content-based vector similarity scoring (evaluating `tags`, `techStack`, `mode` overlap + registration urgency boosts) and writing ranked hackathon IDs directly to `/users/{userId}/recommendations/latest`.

---

## Architecture & Directory Structure

```
services/data-pipeline/
├── requirements.txt         # Python dependencies (scrapy, celery, redis, firebase-admin, pydantic, pytest)
├── README.md                # Service documentation
├── scripts/                 # Standalone executable CLI & cron scripts
│   ├── run_local_scrape.py           # Phase 2: Scrape, deduplicate & save 100+ hackathons to output/
│   ├── run_firestore_ingestion.py    # Phase 3: Synchronous Firestore database ingestion
│   └── run_recommendation_engine.py  # Phase 4: Run recommendation scoring across sample user profiles
├── src/
│   ├── models/              # Pydantic schemas (HackathonDocument, RecommendationDocument, RankedHackathon)
│   ├── normalization/       # Date, currency, text cleaning & dedup hashing (normalizer.py)
│   ├── deduplication/       # DeduplicationEngine & cross-listed record merger (engine.py)
│   ├── crawler/             # Scrapy spiders (DevpostSpider, MLHSpider), middlewares & pipeline
│   ├── firebase/            # Firebase Admin SDK Firestore client & upsert helpers (client.py)
│   ├── scheduler/           # Celery scheduler (celery_app.py) & background tasks (tasks.py)
│   └── recommendation/      # Content similarity engine & recommendation service
└── tests/                   # Automated unit test suite
    ├── test_models.py
    ├── test_normalization.py
    ├── test_spiders.py
    ├── test_deduplication.py
    ├── test_scheduler.py
    └── test_recommendation.py
```

---

## Running Executable Deliverables & Scripts

### 1. Phase 2: Local Scrape & Deduplication (Generate 100+ Clean Records)
```bash
python services/data-pipeline/scripts/run_local_scrape.py
```
*Outputs clean deduplicated records to `services/data-pipeline/output/hackathons_dump.json`.*

### 2. Phase 3: Run Firestore Ingestion
```bash
python services/data-pipeline/scripts/run_firestore_ingestion.py
```
*Executes `run_ingestion_pipeline_task(dry_run=True/False)` to upsert unique records into `/hackathons`.*

### 3. Phase 4: Run Recommendation Engine Simulation
```bash
python services/data-pipeline/scripts/run_recommendation_engine.py
```
*Scores hackathons for sample user profiles (`user_ai_python_01`, `user_web3_rust_02`, `user_mobile_flutter_03`) and saves output to `services/data-pipeline/output/sample_recommendations.json`.*

---

## Running Automated Unit Tests
```bash
pytest services/data-pipeline/tests/ -v
```

# HackMap Data Pipeline & Recommendation Engine (Noor - Track 2 & Track 4)

This service is responsible for:
1. **Scraping Hackathons**: Scrapy-based crawlers targeting global platforms (Devpost, MLH, etc.).
2. **Data Normalization & Deduplication**: Standardizing dates to UTC ISO-8601, normalizing currencies and tags, and deduplicating cross-listed hackathons via similarity hashing.
3. **Firestore Integration**: Upserting normalized records into `/hackathons/{hackathonId}`.
4. **Personalization Engine**: Celery workers running vector similarity scoring (`scikit-learn`, `numpy`) and writing ranked hackathon IDs directly to `/users/{userId}/recommendations/latest`.

## Architecture & Directory Structure

```
services/data-pipeline/
├── requirements.txt         # Python dependencies
├── src/
│   ├── models/              # Pydantic schemas for HackathonDocument & Recommendations
│   ├── normalization/       # Date, currency, text normalization & dedup hashing
│   ├── crawler/             # Scrapy settings, middlewares (user-agent rotation, retries)
│   └── firebase/            # Firebase Admin SDK Firestore client & upsert helpers
└── tests/                   # Automated unit tests for schema validation & normalization
```

## Running Unit Tests
```bash
pytest services/data-pipeline/tests/ -v
```

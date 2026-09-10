# Cursor Offset API

A production-ready FastAPI application demonstrating pagination strategies with **offset-based** and **cursor-based** approaches. The project implements best practices for async Python development, database optimization, caching, and comprehensive testing.

## Features

✨ **Pagination Strategies**
- **Offset-based pagination** — traditional page navigation
- **Cursor-based pagination** — efficient keyset pagination for large datasets

🗄️ **Database & ORM**
- SQLAlchemy 2.0 with async/await support
- PostgreSQL 17 with optimized indexes
- Alembic migrations with auto-generation
- Composite index `(created_at, id)` for cursor pagination performance

🚀 **Performance**
- Redis caching with FastAPI-Cache2
- Smart cache invalidation on mutations
- Rate limiting (5 req/2s by default)
- Load testing with Locust included

🧪 **Testing**
- 93% code coverage with pytest
- Async integration tests with full isolation
- Mock Redis and database fixtures
- Safe test environment validation

📚 **Architecture**
- Clean layered architecture: API → Service → Repository → Models
- Unit of Work pattern for transaction management
- Dependency injection throughout
- Custom exception handlers with structured error responses

⚙️ **Configuration**
- Environment-based settings (LOCAL, TEST, DEV, LOCUST, PROD)
- Docker Compose for development stack
- Type hints and validation with Pydantic

---

## Quick Start

### Prerequisites

- Python 3.14+
- Docker & Docker Compose (or PostgreSQL 17 + Redis 7 installed locally)
- UV package manager (or pip)

### 1. Clone & Setup

```bash
git clone https://github.com/AgasiMir/cursor_offset.git
cd cursor_offset
```

### 2. Install Dependencies

**With UV:**
```bash
uv sync --group dev
```

**With pip:**
```bash
pip install -e ".[dev]"
```

### 3. Start Infrastructure

**Using Docker Compose (recommended):**
```bash
docker compose up -d
```

This starts:
- PostgreSQL (dev) on `localhost:6432`
- PostgreSQL (test) on `localhost:16432`
- PostgreSQL (locust) on `localhost:26432`
- Redis on `localhost:6379`

**Or run PostgreSQL & Redis locally:**
```bash
# PostgreSQL should be running on localhost:5432
# Redis should be running on localhost:6379
```

### 4. Configure Environment

Copy and edit environment files:

```bash
cp .env.example.local .env.local
# Edit .env.local with your database credentials
```

For testing:
```bash
cp .env.example.test .env.test
# Usually TEST environment uses test_db container
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start the Server

```bash
fastapi dev app/main.py
```

Server runs on `http://localhost:8000`

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API Endpoints

All endpoints are under `/v1/posts`

### Offset-Based Pagination

**Get posts with page number:**
```http
GET /v1/posts/offset?page=1&page_size=10
```

Response:
```json
{
  "posts": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Post Title",
      "content": "Post content...",
      "created_at": "2025-09-05T10:30:00+00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 10
  }
}
```

**Parameters:**
- `page` (int, default=1, min=1): Page number
- `page_size` (int, default=5, min=1, max=50): Posts per page

**Cached for 30 seconds**

### Cursor-Based Pagination

**Get posts using cursor:**
```http
GET /v1/posts/cursor?limit=10
```

First page (no cursor):
```http
GET /v1/posts/cursor?limit=10
```

Next pages:
```http
GET /v1/posts/cursor?limit=10&cursor_id=550e8400-e29b-41d4-a716-446655440000&created_at=2025-09-05T10:30:00+00:00
```

Response:
```json
{
  "posts": [...],
  "has_more": true,
  "next_cursor": {
    "last_id": "550e8400-e29b-41d4-a716-446655441111",
    "last_created_at": "2025-09-05T10:28:00+00:00"
  }
}
```

**Parameters:**
- `limit` (int, default=5, min=1, max=50): Posts per page
- `cursor_id` (UUID, optional): ID of last post from previous page
- `created_at` (datetime, optional): Creation time of last post from previous page

**Cached for 30 seconds**

> ⚠️ Both `cursor_id` and `created_at` must be provided together or omitted together

### Get Single Post

```http
GET /v1/posts/{post_id}
```

**Cached for 300 seconds**

### Create Post

```http
POST /v1/posts
Content-Type: application/json

{
  "title": "New Post",
  "content": "Post content (optional)"
}
```

Returns 201 with created post.

### Update Post

```http
PATCH /v1/posts/{post_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content"
}
```

Cache is automatically invalidated.

### Delete Post

```http
DELETE /v1/posts/{post_id}
```

Returns 204 No Content. Cache is automatically invalidated.

---

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=html
```

Opens coverage report in `htmlcov/index.html`

### Run Specific Test File

```bash
pytest tests/test_routers.py -v
```

### Run Tests Matching Pattern

```bash
pytest -k "cursor" -v
```

**Test Files:**
- `tests/test_routers.py` — API endpoint integration tests
- `tests/test_repo.py` — Repository layer tests
- `tests/test_schemas.py` — Schema validation tests
- `tests/test_redis.py` — Redis caching tests
- `tests/test_redis_2.py` — Additional Redis tests
- `tests/test_handlers.py` — Exception handler tests

**Coverage:** 93% of codebase

---

## Performance Testing with Locust

Load testing is built-in using Locust.

### Basic Load Test

```bash
locust -f locustfile.py --host=http://localhost:8000
```

Opens web UI on `http://localhost:8000`. Configure:
- Number of users to simulate
- Spawn rate
- Test duration

### Advanced Performance Test

```bash
locust -f locustfile_perf.py --host=http://localhost:8000 -u 100 -r 10 -t 5m
```

- `-u 100`: 100 concurrent users
- `-r 10`: spawn 10 users per second
- `-t 5m`: run for 5 minutes

**Simulated workload:**
- 8 requests: Offset pagination (pages 1, 82, 320)
- 4 requests: Single post retrieval
- 2 requests: Post creation

---

## Architecture

### Directory Structure

```
cursor_offset/
├── app/
│   ├── main.py                 # FastAPI app initialization & lifespan
│   ├── config.py               # Settings management
│   ├── init.py                 # Redis manager
│   ├── schemas.py              # Pydantic models (requests/responses)
│   ├── uow.py                  # Unit of Work pattern
│   ├── api/
│   │   ├── v1/routers/
│   │   │   └── posts.py        # Post endpoints
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   ├── rate_limit.py       # Rate limiting
│   │   └── handlers.py         # Misc handlers
│   ├── service/
│   │   └── post_service.py     # Business logic
│   ├── repository/
│   │   └── post_repo.py        # Data access layer
│   ├── models/
│   │   └── post.py             # SQLAlchemy ORM model
│   ├── core/
│   │   └── database.py         # DB connection & session factory
│   ├── exception_handlers/
│   │   ├── errors.py           # Exception handlers registration
│   │   ├── python_exceptions.py # Custom exceptions
│   │   └── schemas.py          # Error response model
│   ├── middlewares/
│   │   └── log.py              # Request logging
│   ├── decorators/             # Custom decorators
│   ├── cache_key_builders/     # Cache key strategies
│   └── migrations/             # Alembic migrations
├── tests/                      # Test suite
├── compose.yaml                # Docker Compose config
├── pyproject.toml              # Project metadata & dependencies
├── alembic.ini                 # Alembic configuration
├── pytest.ini                  # Pytest configuration
├── locustfile.py               # Load testing scenarios
└── README.md                   # This file
```

### Design Patterns

**Unit of Work (UoW)**
- Manages database session lifecycle
- Provides automatic rollback on exceptions
- Ensures transactional consistency

```python
async with UnitOfWork(session_factory) as uow:
    result = await uow.posts.create_post(schema)
    # Auto-commit on exit, auto-rollback on exception
```

**Dependency Injection**
- FastAPI's `Depends()` for request-scoped services
- Service layer receives UoW, doesn't create it
- Testable and mockable

```python
async def endpoint(service: PostServiceDep):
    # PostServiceDep is auto-resolved by FastAPI
```

**Repository Pattern**
- Single responsibility: data access
- Query building (offset vs cursor)
- Model-to-schema conversion

**Service Layer**
- Business logic orchestration
- Cache invalidation on mutations
- Minimal logic (mostly delegation)

---

## Database Optimization

### Indexes

**Single column indexes:**
- `posts.id` (primary key)
- `posts.title` (search optimization)
- `posts.created_at` (temporal queries)

**Composite index:**
- `(posts.created_at, posts.id)` DESC — optimizes cursor pagination with index covering

### Query Patterns

**Offset Pagination:**
```sql
SELECT * FROM posts 
ORDER BY created_at DESC 
LIMIT 10 OFFSET 0
```

Issues with large offsets: DB must skip N rows (O(n))

**Cursor Pagination (recommended for large datasets):**
```sql
SELECT * FROM posts 
WHERE created_at < ? OR (created_at = ? AND id < ?)
ORDER BY created_at DESC, id DESC 
LIMIT 11  -- fetch N+1 to detect has_more
```

Advantages:
- O(1) complexity regardless of position
- Consistent results with concurrent updates
- Scalable to billions of rows

---

## Configuration

### Environment Variables

**Local Development (.env.local):**
```env
ENVIRONMENT=LOCAL
DB_DRIVER=postgresql+asyncpg
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=6432
POSTGRES_DB=cursor_offset
REDIS_HOST=localhost
REDIS_PORT=6379
```

**Testing (.env.test):**
```env
ENVIRONMENT=TEST
DB_HOST=localhost
DB_PORT=16432
POSTGRES_DB=cursor_offset_test
```

**Load Testing (.env.locust):**
```env
ENVIRONMENT=LOCUST
DB_HOST=localhost
DB_PORT=26432
POSTGRES_DB=cursor_offset_locust
```

### Environments

| Env | Purpose | Rate Limit | Cache | DB Pool |
|-----|---------|-----------|-------|---------|
| LOCAL | Development | Disabled | Enabled | Regular |
| DEV | Staging | 5 req/2s | Enabled | Regular |
| PROD | Production | 5 req/2s | Enabled | Regular |
| TEST | Testing | Disabled | Mocked | NullPool |
| LOCUST | Load testing | Disabled | Mocked | NullPool |

---

## Caching Strategy

### Cache Keys

**Posts list (offset):**
```
fastapi-cache:post_list:{page}:{page_size}
TTL: 30 seconds
```

**Posts list (cursor):**
```
fastapi-cache:post_list_cursor:{limit}:{cursor_id}:{created_at}
TTL: 30 seconds
```

**Single post:**
```
fastapi-cache:post:{post_id}
TTL: 300 seconds
```

### Cache Invalidation

Automatic invalidation on mutations:

```python
# On POST, PATCH, DELETE
await redis_manager.delete(f"fastapi-cache:post:{post_id}")
```

---

## Development

### Code Quality Tools

**Type checking:**
```bash
mypy app/
```

**Linting & Formatting:**
```bash
ruff check app/
ruff format app/
```

**All checks:**
```bash
pytest --cov
mypy app/
ruff check app/
```

### Adding a New Feature

1. **Create migration:**
   ```bash
   alembic revision --autogenerate -m "add new column"
   alembic upgrade head
   ```

2. **Add ORM model** in `app/models/`

3. **Add repository methods** in `app/repository/`

4. **Add service methods** in `app/service/`

5. **Add API endpoints** in `app/api/v1/routers/`

6. **Add schemas** in `app/schemas.py`

7. **Write tests** in `tests/`

8. **Update cache keys** in `app/cache_key_builders/` if needed

---

## Troubleshooting

### Connection Refused: PostgreSQL

**Problem:** `could not connect to server: Connection refused`

**Solution:**
```bash
# If using Docker Compose
docker compose up -d postgres

# Verify connection
psql -h localhost -p 6432 -U postgres -d cursor_offset
```

### Connection Refused: Redis

**Problem:** `Connection refused` when connecting to Redis

**Solution:**
```bash
# If using Docker Compose
docker compose up -d redis

# Verify connection
redis-cli ping
# Expected: PONG
```

### Tests Fail with "Wrong Environment"

**Problem:** `AssertionError: settings.ENVIRONMENT != "TEST"`

**Solution:**
```bash
# Ensure .env.test is properly loaded
export ENVIRONMENT=TEST
# or in .env.test file
ENVIRONMENT=TEST
```

### Alembic Can't Find Models

**Problem:** `Can't find table/column in migration`

**Solution:**
1. Ensure all models are imported in `app/core/database.py`
2. Run: `alembic revision --autogenerate -m "description"`
3. Review generated migration for correctness

---

## Performance Benchmarks

With 10,000 posts and default hardware:

| Endpoint | Method | Avg Response | p95 | p99 |
|----------|--------|--------------|-----|-----|
| `/offset?page=1` | Cached | 2ms | 5ms | 8ms |
| `/offset?page=1000` | Cached | 2ms | 5ms | 8ms |
| `/cursor?limit=10` | Cached | 2ms | 5ms | 8ms |
| `/{id}` | Cached | 1ms | 3ms | 5ms |
| POST | No cache | 15ms | 25ms | 40ms |

> Benchmarks from `locustfile_perf.py` with 100 concurrent users
> Times include network round-trip

---

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and write tests
3. Run checks: `pytest --cov && mypy app/ && ruff check app/`
4. Create pull request

---

## License

MIT License — see LICENSE file

---

## Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Cursor-Based Pagination Best Practices](https://use-the-index-luke.com/sql/partial-results/keyset-pagination)
- [Redis Caching Patterns](https://docs.redis.com/latest/develop/use-redis-with-python/)
- [Alembic Migrations Guide](https://alembic.sqlalchemy.org/)

---

**Last Updated:** September 2025  
**Author:** AgasiMir  
**Version:** 0.1.0

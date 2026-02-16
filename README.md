# FastAPI Microservices Playground (Main / Payment / Backend)

This repo is a starter for running 3 FastAPI microservices with a shared Kafka event bus.

## Structure

- `services/main_service`: main domain service
- `services/payment_service`: payment domain service
- `services/backend_service`: admin/backend service
- `common/kafka_client.py`: shared Kafka producer/consumer manager
- `docker-compose.yml`: local MySQL + Redis + Kafka
- `alembic/`: migration scripts and revisions
- `alembic.ini`: Alembic config entrypoint

## 1) Create Conda Environment

```bash
conda env create -f environment.yml
conda activate microservices-kafka
```

Or use pip directly:

```bash
pip install -r requirements.txt
```

## 2) Configure Environment Variables

```bash
cp .env.example .env
```

Use a different `KAFKA_GROUP_ID` in each terminal when starting services.
Set JWT variables for member registration token:

```bash
export JWT_SECRET_KEY=replace-with-strong-secret
export JWT_ALGORITHM=HS256
export JWT_EXPIRE_MINUTES=120
```

## 3) Start Infrastructure (MySQL / Redis / Kafka)

```bash
docker compose up -d
```

Default ports in this setup:

- MySQL: `localhost:3333`
- Redis: `localhost:6633`
- Kafka: `localhost:9092`

MySQL default database name: `kafka`

## 4) Run Database Migrations

```bash
alembic upgrade head
```

Create a new migration revision when schema changes:

```bash
alembic revision -m "your message"
```

## 5) Run Services

From repo root:

```bash
PYTHONPATH=. KAFKA_GROUP_ID=main-group uvicorn services.main_service.app.main:app --reload --port 8001
PYTHONPATH=. KAFKA_GROUP_ID=payment-group uvicorn services.payment_service.app.main:app --reload --port 8002
PYTHONPATH=. KAFKA_GROUP_ID=backend-group uvicorn services.backend_service.app.main:app --reload --port 8003
```

## 6) Quick Test

Publish an event from payment service:

```bash
curl -X POST http://127.0.0.1:8002/events \
  -H "content-type: application/json" \
  -d '{
    "event_type": "payment.updated",
    "entity": "payment",
    "entity_id": "pay_123",
    "version": 1
  }'
```

You should see logs in other services consuming the same event from Kafka.

Register member on main service:

```bash
curl -X POST http://127.0.0.1:8001/members/register \
  -H "content-type: application/json" \
  -d '{
    "account": "ken",
    "password": "1234567890"
  }'
```

Login member on main service:

```bash
curl -X POST http://127.0.0.1:8001/members/login \
  -H "content-type: application/json" \
  -d '{
    "account": "ken",
    "password": "1234567890"
  }'
```

## 7) Run Tests

```bash
pytest -q
```

Test layout:

- Unit tests: `services/main_service/test/unit` (all mocks / fake connections)
- Integration tests: `services/main_service/test/controller`
- Shared fixtures and fake connections: `services/main_service/test/conftest.py`

Integration test notes:

- Uses real MySQL database (no fake DB).
- For each integration test: drop DB -> create DB -> run `alembic upgrade head` -> test -> drop DB.
- Configure DB connection in `services/main_service/test.env`.
- If MySQL is unavailable, integration tests are skipped.

## Next Step

After this base is running, add:

1. MySQL write + outbox table in each write flow
2. Redis cache invalidation keys by event type
3. idempotency table keyed by `event_id`

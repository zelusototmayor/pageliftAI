# PageLift AI Backend

## Quickstart

### 1. Clone and configure

```bash
git clone <repo-url>
cd PageLift\ AI
cp .env.example .env
```

### 2. Start services

```bash
docker-compose up --build
```

### 3. Run tests

```bash
docker-compose exec api pytest
```

## Endpoints
- `GET /healthz` — health check

## Configuration
See `.env.example` for all environment variables. 
# 🐳 Docker Setup Guide

Complete guide for running Gmail Document Scraper with Docker.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 2. Build and run
docker-compose up

# 3. Run in interactive mode
docker-compose run --rm gmail-scraper --interactive
```

### Using Docker CLI

```bash
# Build image
docker build -t gmail-doc-scraper .

# Run with environment file
docker run --env-file .env gmail-doc-scraper --interactive

# Run with inline environment variables
docker run -e GMAIL_EMAIL=your-email@gmail.com \
           -e GMAIL_APP_PASSWORD=your-password \
           gmail-doc-scraper --interactive
```

## Configuration

### Environment Variables

Create `.env` file:

```bash
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
OUTPUT_DIR=/app/output
```

### Volume Mounts

Mount volumes to persist data:

```bash
docker run --env-file .env \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/config:/app/config \
  gmail-doc-scraper --interactive
```

## Docker Compose Configuration

### docker-compose.yml

```yaml
version: '3.8'

services:
  gmail-scraper:
    build: .
    env_file:
      - .env
    volumes:
      - ./output:/app/output
      - ./reports:/app/reports
      - ./config:/app/config
    stdin_open: true
    tty: true
```

### Running Commands

```bash
# Interactive mode
docker-compose run --rm gmail-scraper --interactive

# Resume from checkpoint
docker-compose run --rm gmail-scraper --resume

# Specific date range
docker-compose run --rm gmail-scraper \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --document-types invoices

# Dry run
docker-compose run --rm gmail-scraper --dry-run
```

## Production Deployment

### Build for Production

```bash
# Build image
docker build -t gmail-doc-scraper:1.0.0 .

# Tag for registry
docker tag gmail-doc-scraper:1.0.0 your-registry/gmail-doc-scraper:1.0.0

# Push to registry
docker push your-registry/gmail-doc-scraper:1.0.0
```

### Run in Background

```bash
# Detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Scheduled Runs (Cron)

Create a cron job:

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/gmail-doc-scrapper && docker-compose run --rm gmail-scraper --resume
```

Or use Docker with cron:

```dockerfile
FROM gmail-doc-scraper:1.0.0

# Install cron
RUN apt-get update && apt-get install -y cron

# Add cron job
RUN echo "0 2 * * * python /app/main.py --resume" > /etc/cron.d/scraper-cron
RUN chmod 0644 /etc/cron.d/scraper-cron
RUN crontab /etc/cron.d/scraper-cron

CMD ["cron", "-f"]
```

## Troubleshooting

### Container Exits Immediately

```bash
# Check logs
docker-compose logs

# Run with shell access
docker-compose run --rm --entrypoint /bin/bash gmail-scraper
```

### Permission Issues

```bash
# Run with current user
docker-compose run --rm --user $(id -u):$(id -g) gmail-scraper --interactive
```

### Out of Memory

Increase Docker memory limit:

```yaml
# docker-compose.yml
services:
  gmail-scraper:
    mem_limit: 4g
    memswap_limit: 4g
```

### Network Issues

```bash
# Use host network
docker run --network host --env-file .env gmail-doc-scraper --interactive
```

## Advanced Configuration

### Multi-Stage Build

Optimize image size:

```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
RUN python -m spacy download pt_core_news_lg

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
```

### Health Checks

```yaml
# docker-compose.yml
services:
  gmail-scraper:
    healthcheck:
      test: ["CMD", "python", "test_installation.py"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Environment-Specific Configs

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gmail-doc-scraper
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gmail-doc-scraper
  template:
    metadata:
      labels:
        app: gmail-doc-scraper
    spec:
      containers:
      - name: scraper
        image: gmail-doc-scraper:1.0.0
        env:
        - name: GMAIL_EMAIL
          valueFrom:
            secretKeyRef:
              name: gmail-credentials
              key: email
        - name: GMAIL_APP_PASSWORD
          valueFrom:
            secretKeyRef:
              name: gmail-credentials
              key: password
        volumeMounts:
        - name: output
          mountPath: /app/output
        - name: reports
          mountPath: /app/reports
      volumes:
      - name: output
        persistentVolumeClaim:
          claimName: scraper-output
      - name: reports
        persistentVolumeClaim:
          claimName: scraper-reports
```

### Create Secret

```bash
kubectl create secret generic gmail-credentials \
  --from-literal=email=your-email@gmail.com \
  --from-literal=password=your-app-password
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push Docker Image

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build image
        run: docker build -t gmail-doc-scraper:${{ github.ref_name }} .

      - name: Push to registry
        run: |
          docker tag gmail-doc-scraper:${{ github.ref_name }} \
            your-registry/gmail-doc-scraper:${{ github.ref_name }}
          docker push your-registry/gmail-doc-scraper:${{ github.ref_name }}
```

## Security Best Practices

1. **Never commit .env file**
   - Use `.env.example` as template
   - Add `.env` to `.gitignore`

2. **Use secrets management**
   ```bash
   # Docker Swarm
   docker secret create gmail_email your-email@gmail.com
   docker secret create gmail_password your-app-password
   ```

3. **Run as non-root user**
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

4. **Scan images for vulnerabilities**
   ```bash
   docker scan gmail-doc-scraper:latest
   ```

## Performance Optimization

### Resource Limits

```yaml
# docker-compose.yml
services:
  gmail-scraper:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Build Cache

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker build -t gmail-doc-scraper .
```

## Monitoring

### Logs

```bash
# Follow logs
docker-compose logs -f

# Export logs
docker-compose logs > scraper.log

# View last 100 lines
docker-compose logs --tail 100
```

### Metrics

```bash
# Container stats
docker stats gmail-doc-scraper

# Inspect container
docker inspect gmail-doc-scraper
```

## Support

For Docker-specific issues, contact:
**Email:** joao.fernandes@docdigitizer.com

---

**Last Updated:** 2026-01-02

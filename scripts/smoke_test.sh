#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "Checking root endpoint..."
curl -fsS "${BASE_URL}/" | python -m json.tool

echo "Checking liveness..."
curl -fsS "${BASE_URL}/health/live" | python -m json.tool

echo "Checking readiness..."
curl -fsS "${BASE_URL}/health/ready" | python -m json.tool

echo "Creating task..."
curl -fsS -X POST "${BASE_URL}/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title":"Smoke test task","description":"Created by scripts/smoke_test.sh"}' \
  | python -m json.tool

echo "Listing tasks..."
curl -fsS "${BASE_URL}/tasks" | python -m json.tool

echo "OK"

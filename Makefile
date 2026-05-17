.PHONY: install run migrate downgrade test lint format

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade -1

test:
	pytest -q

lint:
	ruff check .

format:
	ruff format .

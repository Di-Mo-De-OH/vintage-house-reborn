.PHONY: format type test coverage check

format:
	docker compose exec fastapi uv run black .
	docker compose exec fastapi uv run ruff check . --fix

type:
	docker compose exec fastapi uv run mypy app

check:
	docker compose exec fastapi uv run black .
	docker compose exec fastapi uv run ruff check . --fix
	docker compose exec fastapi uv run mypy app
	docker compose exec fastapi uv run coverage run -m pytest
	docker compose exec fastapi uv run coverage report
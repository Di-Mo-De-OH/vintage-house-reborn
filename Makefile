.PHONY: format type test coverage coverage-html check

format:
	docker compose exec fastapi uv run black .
	docker compose exec fastapi uv run ruff check . --fix

type:
	docker compose exec fastapi uv run mypy app

TEST_ENV := -e POSTGRES_DB=vintage-house_test -e REDIS_DB=1

test:
	docker compose exec $(TEST_ENV) fastapi uv run coverage run -m pytest

coverage:
	docker compose exec $(TEST_ENV) fastapi uv run coverage report -m

coverage-html:
	docker compose exec fastapi uv run coverage html
	open htmlcov/index.html

check:
	docker compose exec fastapi uv run black .
	docker compose exec fastapi uv run ruff check . --fix
	docker compose exec fastapi uv run mypy app
	docker compose exec $(TEST_ENV) fastapi uv run coverage run -m pytest
	docker compose exec $(TEST_ENV) fastapi uv run coverage report -m
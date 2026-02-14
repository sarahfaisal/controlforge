.PHONY: api web up lint-packs

api:
	cd apps/api && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && \
	TRUSTSTACK_CONFIG_ROOT=../../registry TRUSTSTACK_WORKSPACE_ROOT=../../workspaces \
	uvicorn truststack_grc.main:app --reload --port 8000

web:
	cd apps/web && npm install && npm run dev

up:
	docker compose up --build

lint-packs:
	cd apps/api && python -m truststack_grc.cli lint-packs --root ../../registry/packs

# ============================================
# GeoSDI Geothermal v2.0 - Makefile (Anaconda)
# ============================================

.PHONY: help activate install up down logs test lint format clean

help:
	@echo "GeoSDI Geothermal v2.0 - Available commands:"
	@echo "  make install  - Install dependencies via conda"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linters"
	@echo "  make format   - Format code"
	@echo "  make clean    - Clean temporary files"
	@echo "  make env      - Show current conda env"

env:
	@conda info --envs
	@echo ""
	@python --version
	@which python

install:
	conda install -y -c conda-forge numpy pandas scipy polars geopandas shapely
	conda install -y -c conda-forge rasterio pyproj fiona psycopg2 sqlalchemy
	conda install -y -c conda-forge scikit-learn xgboost lightgbm networkx
	pip install -r requirements.txt

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	pytest tests/ -v --cov=src

lint:
	ruff check src/
	mypy src/

format:
	black src/
	ruff check --fix src/

clean:
	Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
	Get-ChildItem -Path . -Recurse -File -Include "*.pyc" | Remove-Item -Force
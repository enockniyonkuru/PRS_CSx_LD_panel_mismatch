.PHONY: help install test lint format clean generate

help:
	@echo "PRS-CSx Figure 4 - Available Commands"
	@echo "======================================"
	@echo "make install    - Install dependencies"
	@echo "make test       - Run tests"
	@echo "make lint       - Run code linter (flake8)"
	@echo "make format     - Format code with black"
	@echo "make generate   - Generate Figure 4 from sample data"
	@echo "make clean      - Remove generated files and cache"
	@echo "make help       - Show this help message"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest -v

lint:
	flake8 src/ --max-line-length=100

format:
	black src/ --line-length=100

generate:
	python src/generate_figure4.py \
		--input data/sample_results.csv \
		--output outputs/Figure4_PopulationStratified_Extended.png

clean:
	rm -rf outputs/*.png outputs/*.pdf
	rm -rf __pycache__ .pytest_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

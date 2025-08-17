install:
	pip install -r requirements.txt

run:
	python app/main.py

test:
	pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
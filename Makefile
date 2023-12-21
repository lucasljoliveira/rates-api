update-precommit:
	poetry run pre-commit install && poetry run pre-commit autoupdate

lint:
	poetry run pre-commit run

test:
	poetry run pytest -s rates --cov=rates/apps -l --cov-report term-missing

dc-project-up:
	docker-compose up app

dc-project-test:
	docker-compose up test

PIPENV_RUN := pipenv run

isort-src:
	$(PIPENV_RUN) isort -rc ./fastapi_users

isort-docs:
	$(PIPENV_RUN) isort -rc ./docs/src -o fastapi_users

format: isort-src isort-docs
	$(PIPENV_RUN) black .

test:
	$(PIPENV_RUN) pytest --cov=fastapi_users/

docs-serve:
	$(PIPENV_RUN) mkdocs serve

docs-publish:
	$(PIPENV_RUN) mkdocs gh-deploy

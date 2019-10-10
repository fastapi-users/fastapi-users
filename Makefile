PIPENV_RUN := pipenv run

format:
	$(PIPENV_RUN) isort -rc .
	$(PIPENV_RUN) black .

test:
	$(PIPENV_RUN) pytest

docs-serve:
	$(PIPENV_RUN) mkdocs serve

docs-publish:
	$(PIPENV_RUN) mkdocs gh-deploy

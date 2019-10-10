PIPENV_RUN := pipenv run

format:
	$(PIPENV_RUN) isort -rc .
	$(PIPENV_RUN) black .

test:
	$(PIPENV_RUN) pytest

PIPENV_RUN := pipenv run
MONGODB_CONTAINER_NAME := fastapi-users-test-mongo

isort-src:
	$(PIPENV_RUN) isort ./fastapi_users ./tests

isort-docs:
	$(PIPENV_RUN) isort ./docs/src -o fastapi_users

format: isort-src isort-docs
	$(PIPENV_RUN) black .

test:
	docker stop $(MONGODB_CONTAINER_NAME) || true
	docker run -d --rm --name $(MONGODB_CONTAINER_NAME) -p 27017:27017 mongo:4.2
	$(PIPENV_RUN) pytest --cov=fastapi_users/ --cov-report=term-missing
	docker stop $(MONGODB_CONTAINER_NAME)

docs-serve:
	$(PIPENV_RUN) mkdocs serve

docs-publish:
	$(PIPENV_RUN) mkdocs gh-deploy

bumpversion-major:
	$(PIPENV_RUN) bumpversion major

bumpversion-minor:
	$(PIPENV_RUN) bumpversion minor

bumpversion-patch:
	$(PIPENV_RUN) bumpversion patch

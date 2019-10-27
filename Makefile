PIPENV_RUN := pipenv run
MONGODB_CONTAINER_NAME := fastapi-users-test-mongo

isort-src:
	$(PIPENV_RUN) isort -rc ./fastapi_users

isort-docs:
	$(PIPENV_RUN) isort -rc ./docs/src -o fastapi_users

format: isort-src isort-docs
	$(PIPENV_RUN) black .

test:
	docker run -d --rm --name $(MONGODB_CONTAINER_NAME) -p 27017:27017 mvertes/alpine-mongo
	$(PIPENV_RUN) pytest --cov=fastapi_users/
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

MONGODB_CONTAINER_NAME := fastapi-users-test-mongo

isort-src:
	isort ./fastapi_users ./tests

isort-docs:
	isort ./docs/src -o fastapi_users

format: isort-src isort-docs
	black .

test:
	docker stop $(MONGODB_CONTAINER_NAME) || true
	docker run -d --rm --name $(MONGODB_CONTAINER_NAME) -p 27017:27017 mongo:4.2
	pytest --cov=fastapi_users/ --cov-report=term-missing --cov-fail-under=100
	docker stop $(MONGODB_CONTAINER_NAME)

docs-serve:
	mkdocs serve

docs-publish:
	mkdocs gh-deploy

bumpversion-major:
	bumpversion major

bumpversion-minor:
	bumpversion minor

bumpversion-patch:
	bumpversion patch

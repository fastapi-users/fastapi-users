isort-src:
	isort ./fastapi_users ./tests

isort-docs:
	isort ./docs/src -o fastapi_users

isort-examples:
	isort ./examples -o fastapi_users -p app

format: isort-src isort-docs isort-examples
	black .

isort-src-check:
	isort --check-only ./fastapi_users ./tests

isort-docs-check:
	isort --check-only ./docs/src -o fastapi_users

isort-examples-check:
	isort --check-only ./examples -o fastapi_users -p app

format-check: isort-src-check isort-docs-check isort-examples-check
	black --check .

lint:
	flake8 ./fastapi_users ./tests

typecheck:
	mypy fastapi_users/

test:
	pytest --cov=fastapi_users/ --cov-report=term-missing --cov-fail-under=100

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

isort-src:
	isort ./fastapi_users ./tests

isort-docs:
	isort ./docs/src -o fastapi_users

format: isort-src isort-docs
	black .

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

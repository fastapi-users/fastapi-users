venv:
	mamba env create -f environment.yml --force

publish:
	rm -rf dist && python -m build && twine upload --repository-url https://pkgs.dev.azure.com/slavo0279/Filuta/_packaging/private-pypi/pypi/upload dist/*.tar.gz

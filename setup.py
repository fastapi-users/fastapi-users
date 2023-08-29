import setuptools


def get_version(version_file: str) -> str:
    with open(version_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


pkg_version = get_version("src/filuta_fastapi_users/__init__.py")

setuptools.setup(
    name="filuta_fastapi_users",
    version=pkg_version,
    author="Josef Ryzi",
    author_email="josef@filuta.ai",
    description="Filuta fork of fastapi-users to include OTP natively",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi >=0.65.2",
        "passlib[bcrypt] ==1.7.4",
        "email-validator >=1.1.0,<2.1",
        "pyjwt[crypto] ==2.8.0",
        "python-multipart ==0.0.6",
        "makefun >=1.11.2,<2.0.0",
        "pydantic<2",
        "python-dotenv",
        "sqlalchemy",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Framework :: FastAPI",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: Session",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    include_package_data=True,
)

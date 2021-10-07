import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycachuser",
    version="0.0.2",
    author="Tom Moran",
    author_email="tommorancodes@gmail.com",
    description="Grabs and stores credentials in a human-readable yaml file, with passwords saved using the keyring module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atommoran/pycachu",
    project_urls={
        "Bug Tracker": "https://github.com/atommoran/pycachu/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
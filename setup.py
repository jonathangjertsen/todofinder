from setuptools import setup, find_packages

if __name__ == "__main__":
    with open("VERSION.txt") as version_file:
        version = version_file.read().strip()

    with open("README.md", "r") as readme_file:
        long_description = readme_file.read()

    setup(
        name="todofinder",
        version=version,
        description="Scan for TODO's",
        url="https://github.com/jonathangjertsen/todofinder",
        author="Jonathan Reichelt Gjertsen",
        author_email="jonath.re@gmail.com",
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=find_packages(),
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: Implementation :: CPython",
        ],
        license="MIT",
        zip_safe=False,
        project_urls={
            "Documentation": "https://github.com/jonathangjertsen/todofinder",
            "Source": "https://github.com/jonathangjertsen/todofinder",
        },
    )
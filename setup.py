from setuptools import find_packages, setup

# Read the contents of the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fsearch",
    version="0.1.0",
    author="Jimmycliff Obonyo",
    author_email="cliffjimmy27@gmail.com",
    description="A highly performant and secure command-line server to search text files for strings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: Software Development",
    ],
    license="MIT license",
    python_requires=">=3.9",
    extras_require={
        "benchmark": ["matplotlib", "weasyprint"],
        "tests": ["pytest>=6.4.4", "pytest-cov==4.1.0"],
    },
    entry_points={
        "console_scripts": [
            "fsearch=fsearch.__main__:main",
            "fsearch.service=fsearch.service:main",
            "fsearch.client=fsearch.client:main",
            "fsearch.benchmark=fsearch.benchmark:main",
        ]
    },
)

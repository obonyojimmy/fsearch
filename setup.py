from setuptools import setup, find_packages

# Read the contents of the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the dependencies from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.readlines()
    requirements = [req.strip() for req in requirements if req.strip()]

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
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT license',
    python_requires='>=3.7',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'fsearch=fsearch.__main__:main',
        ],
    },
)

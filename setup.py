import setuptools

with open("README.md") as file:
    readme_contents = file.read()

setuptools.setup(
    name="skiddie",
    version="0.1",
    description="Hollywood-style hacking minigames",
    long_description=readme_contents,
    long_description_content_type="text/markdown",
    url="https://github.com/lostatc/skiddie",
    author="Wren Powell",
    author_email="wrenp@duck.com",
    license="GPLv3",
    install_requires=["prompt_toolkit>=2.0.0", "click>=6.0"],
    python_requires=">=3.5",
    tests_require=[],
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Environment :: Console",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ),
    entry_points={
        "console_scripts": [
            "skiddie=skiddie.launcher.cli:cli"
        ]
    },
)

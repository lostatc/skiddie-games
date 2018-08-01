import setuptools

with open("README.rst") as file:
    readme_contents = file.read()

setuptools.setup(
    name="crackit",
    version="0.1",
    description="Hollywood-style hacking minigames",
    long_description=readme_contents,
    long_description_content_type="text/x-rst",
    url="https://github.com/lostatc/crackit",
    author="Wren Powell",
    author_email="wrenp@duck.com",
    license="GPLv3",
    install_requires=["prompt_toolkit", "click"],
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
            "crackit=crackit.launcher.cli:cli"
        ]
    },
)

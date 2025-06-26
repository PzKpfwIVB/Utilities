from setuptools import find_packages, setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="utils_qt_mk",
    version="1.0.5",
    description="Collection of utilities for Qt applications",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=False,
    package_data={'utils_qt_mk': ['colour_list.json']},
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PzKpfwIVB/Utilities',
    author="Mihaly Konda",
    author_email='mihaly.konda@gmail.com',
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
    install_requires=["PySide6 == 6.6.2"],
    extras_require={
        "dev": ["twine >= 6.1.0"],
    },
    python_requires=">= 3.12",
)
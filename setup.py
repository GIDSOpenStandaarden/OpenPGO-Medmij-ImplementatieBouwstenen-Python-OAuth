import setuptools
import pathlib
import re

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open('medmij_oauth/__init__.py') as fp:
    txt = fp.read()

try:
    version = re.findall(r"^__version__ = '([^']+)'\r?$",
                         txt, re.M)[0]
except IndexError:
    raise RuntimeError('Unable to determine version.')

with open('requirements.txt') as fp:
    install_requires = fp.read()

setuptools.setup(
    name="medmij-oauth",
    version=version,
    author="Bas Kloosterman",
    author_email="bask@whiteboxsystems.nl",
    description="Libraries for oauth client/server implementations according to the MedMij requirements",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python-OAuth",
    license='AGPLv3',
    python_requires='>=3.6',
    install_requires=install_requires.split('\n'),
    packages=setuptools.find_packages(exclude=(
        'client_implementation',
        'server_implementation',
        'client_implementation.*',
        'server_implementation.*',
        'tests'
    )),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Healthcare Industry"
    ]
)
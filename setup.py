import setuptools
import pathlib
import re
here = pathlib.Path(__file__).parent

with open("README.rst", "r") as fh:
    long_description = fh.read()

txt = (here / 'medmij_oauth' / '__init__.py').read_text('utf-8')

try:
    version = re.findall(r"^__version__ = '([^']+)'\r?$",
                         txt, re.M)[0]
except IndexError:
    raise RuntimeError('Unable to determine version.')

setuptools.setup(
    name="medmij_oauth",
    version="0.0.1",
    author="Bas Kloosterman",
    author_email="bask@whiteboxsystems.nl",
    description="Libraries for oauth client/server implementations according to the MedMij requirements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/baskloosterman/medmij_oauth",
    license='AGPLv3',
    python_requires='>=3.6',
    packages=setuptools.find_packages(exclude=(
        'client_implementation',
        'server_implementation',
        'client_implementation.*',
        'server_implementation.*',
        'tests'
    )),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        "Operating System :: OS Independent",
        "Intended Audience :: Healthcare Industry",
        "Development Status :: 1 - Planning"
    ],
)
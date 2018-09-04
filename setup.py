import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="medmij_oauth",
    version="0.0.1",
    author="Bas Kloosterman",
    author_email="bask@whiteboxsystems.nl",
    description="Libraries for oauth client/server implementations complying to the MedMij requirements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/baskloosterman/medmij_oauth",
    packages=['medmij_oauth', 'medmij_oauth.client', 'medmij_oauth.server', 'medmij_oauth.exceptions'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        "Operating System :: OS Independent",
        "Intended Audience :: Healthcare Industry",
        "Development Status :: 1 - Planning"
    ],
)
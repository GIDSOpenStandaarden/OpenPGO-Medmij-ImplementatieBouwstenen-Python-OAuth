.. image:: https://readthedocs.org/projects/openpgo-medmij-implementatiebouwstenen-python-oauth/badge/?version=latest
    :target: https://openpgo-medmij-implementatiebouwstenen-python-oauth.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python-OAuth.svg?branch=master
    :target: https://travis-ci.org/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python-OAuth

.. image:: https://sonarcloud.io/api/project_badges/measure?project=OpenPGO_Python_OAuth&metric=alert_status
    :target: https://sonarcloud.io/dashboard?id=OpenPGO_Python_OAuth

.. image:: https://img.shields.io/badge/License-AGPL%20v3-blue.svg
    :target: https://www.gnu.org/licenses/agpl-3.0


Welcome to MedMij OAuth's documentation
=======================================

The medmij_oauth package assists in implementing an oauth server/client application conform the medmij oauth flow (`described below <https://medmij-oauth.readthedocs.io/en/latest/#the-medmij-oauth-flow>`__). The module consists of 3 main submodules i.e. `medmij_oauth.server <https://medmij-oauth.readthedocs.io/en/latest/welcome.html#server>`__, `medmij_oauth.client <https://medmij-oauth.readthedocs.io/en/latest/welcome.html#client>`__ and `medmij_oauth.exceptions <https://medmij-oauth.readthedocs.io/en/latest/welcome.html#exceptions>`__ .
The client and server submodules are build for use with an async library like `aiohttp <https://github.com/aio-libs/aiohttp>`__.

Beside the package there are two example implementations available on the `github repo <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python-OAuth>`__, an oauth server and client implementation built using these modules (Only a reference, not for production use!).

Read the full documentation on `readthedocs <https://openpgo-medmij-implementatiebouwstenen-python-oauth.readthedocs.io/en/latest/welcome.html>`__.

Installation
============

.. code:: bash

    $ pip install medmij-oauth

Tests
=====

.. code:: bash

    $ pytest -v

Requirements
============

Modules
-------
- Python >=3.7

Example implementations
-----------------------
- aiohttp==3.3.2
- aiohttp-jinja2==1.0.0
- aiohttp-session>=2.7.0
- cryptography==2.3
- SQLAlchemy>=1.3.0

Tests
-----
- pytest==3.7.1
- pytest-asyncio==0.9.0

License
=======
This project is licensed under the AGPL-3.0 License - see the LICENSE file for details

Version Guidance
================

This library follows `Semantic Versioning <https://semver.org/>`__.
The versions of the Afsprakenset are mapped to the versions of the library as follows:

+-------------------------------------------+------------+-----------------+
| Version Afsprakenset                      | Status     | Version library |
+===========================================+============+=================+
| `Afsprakenset 1.1 <afsprakenset11_>`__    | Latest     | 0.1.*           |
+-------------------------------------------+------------+-----------------+

.. _afsprakenset11: https://afsprakenstelsel.medmij.nl/display/PUBLIC/Afsprakenset+release+1.1
.. image:: https://travis-ci.org/BasKloosterman/medmij_oauth.svg?branch=master
    :target: https://travis-ci.org/BasKloosterman/medmij_oauth

Welcome to MedMij OAuth's documentation
=======================================

The medmij_oauth package assists in implementing an oauth server/client application conform the medmij oauth flow (`described below <https://medmij-oauth.readthedocs.io/en/latest/#the-medmij-oauth-flow>`__). The module consists of 3 main submodules i.e. `medmij_oauth.server <https://medmij-oauth.readthedocs.io/en/latest/welcome.html#server>`__, `medmij_oauth.client <https://medmij-oauth.readthedocs.io/en/latest/welcome.html#client>`__ and `medmij_oauth.exceptions <https://medmij-oauth.readthedocs.io/en/latest/welcome.html#exceptions>`__ .
The client and server submodules are build for use with an async library like `aiohttp <https://github.com/aio-libs/aiohttp>`__.

Beside the package there are two example implementations available on the `github repo <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python-OAuth>`__, an oauth server and client implementation built using these modules (Only a reference, not for production use!).

Read the full documentation on `readthedocs <https://medmij-oauth.readthedocs.io/en/latest/welcome.html>`__.

Tests
=====

.. code:: python

    $ pytest -v

Requirements
============

Modules
-------
- Python >=3.6

Example implementations
-----------------------
- aiohttp==3.3.2
- aiohttp-jinja2==1.0.0
- aiohttp-session==2.5.1
- cryptography==2.3
- SQLAlchemy==1.2.10

Tests
-----
- pytest==3.7.1
- pytest-asyncio==0.9.0
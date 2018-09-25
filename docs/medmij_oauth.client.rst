medmij\_oauth.client module
============================


Client
------
.. autoclass:: medmij_oauth.client.Client
    :members:

ZAL (Zorgaanbiederslijst)
-------------------------
.. autofunction:: medmij_oauth.client.parse_zal

.. autoclass:: medmij_oauth.client.ZAL
    :members:

.. autoclass:: medmij_oauth.client.Zorgaanbieder
    :members:

.. autoclass:: medmij_oauth.client.Gegevensdienst
    :members:

GNL (Gegevensdienstnamenlijst)
------------------------------
.. autofunction:: medmij_oauth.client.parse_gnl

Datastore
---------
.. autoclass:: medmij_oauth.client.DataStore
    :members:
    :show-inheritance:

.. _OAuthSession:

OAuthSession
------------

Class that should be implemented by implementor of the OAuth client.
This class is should be instantiated by your implementation of the DataStore base class and represents the current state of an OAuth Session.

The OAuthSession should at least have the following attributes:

- **id** (uuid)
- **state** (string)
- **scope** (string)
- **za_name** (string)
- **gegevensdienst_id** (string)
- **authorization_code** (string)
- **authorized** (boolean)
- **access_token** (string)

Here is a `example implementation <_modules/medmij_oauth/client/data_store.html#OAuthSession/>`__

medmij\_oauth.server module
============================


Server
------
.. autoclass:: medmij_oauth.server.Server
    :members:

OCL (OAuth client lijst)
------------------------
.. autofunction:: medmij_oauth.server.parse_ocl

.. autoclass:: medmij_oauth.server.OCL
    :members:

Datastore
---------
.. autoclass:: medmij_oauth.server.DataStore
    :members:
    :show-inheritance:

.. _OAuthSession:

OAuthSession
------------

Class that should be implemented by implementor of the OAuth Server.
This class is should be instantiated by your implementation of the DataStore base class and represents the current state of your OAuth Session.

The OAuthSession should at least have the following attributes:

- **id** (uuid)
- **response_type** (string)
- **client_id** (string)
- **scope** (string)
- **state** (string)
- **redirect_uri** (string)
- **authorization_code** (string)
- **authorization_code_expiration** (datetime.datetime)
- **authorization_granted** (boolean)
- **access_token** (string)
- **access_token_expiration** (datetime.datetime)
- **client_bsn** (string)

Here is an `example implementation </_modules/medmij_oauth/server/data_store.html#OAuthSession/>`__

.. module:: medmij_oauth.server

medmij\_oauth.server module
============================

Server
------
.. autoclass:: medmij_oauth.server.Server
    :members:

Datastore
---------
.. autoclass:: medmij_oauth.server.DataStore
    :members:
    :show-inheritance:

.. _server.oauthsession:

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
- **zorggebruiker_bsn** (string)

Example implementation:

.. code:: python

    class OAuthSession():
        def __init__(self, response_type, client_id, redirect_uri, scope, state):
            self.id = str(uuid.uuid4())
            self.response_type = response_type
            self.client_id = client_id
            self.scope = scope
            self.state = state
            self.redirect_uri = redirect_uri
            self.created_at = datetime.datetime.now()
            self.authorization_code = None
            self.authorization_code_expiration = -1
            self.authorization_granted = False
            self.access_token = None
            self.access_token_expiration = -1
            self.zorggebruiker_bsn = ''

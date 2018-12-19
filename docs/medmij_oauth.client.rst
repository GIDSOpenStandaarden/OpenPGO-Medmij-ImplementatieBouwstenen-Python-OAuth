.. module:: medmij_oauth.client

medmij\_oauth.client module
============================

Client
------
.. autoclass:: medmij_oauth.client.Client
    :members:

Datastore
---------
.. autoclass:: medmij_oauth.client.DataStore
    :members:
    :show-inheritance:

.. _client.oauthsession:

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


Example implementation:

.. code:: python

    class OAuthSession():
        def __init__(self, state, za_name, gegevensdienst_id, scope):
            self.id = str(uuid.uuid4())
            self.state = state
            self.scope = scope
            self.za_name = za_name
            self.gegevensdienst_id = gegevensdienst_id
            self.authorization_code = None
            self.authorized = False
            self.access_token = None

import urllib.parse
import secrets

from . import validation

from .data_store import DataStore

class Client:
    """
    Class to assist in the OAuth clientside flow

    :type data_store: :class:`DataStore <medmij_oauth.client.DataStore>`
    :param data_store: Must be subclass of DataStore, handles data interaction with
        OAuthSessions see :class:`DataStore <medmij_oauth.client.DataStore>`
        for more info.

    :type get_zal: coroutine
    :param get_zal: Function that returns a
        `ZAL <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__

    :type get_gnl: coroutine
    :param get_gnl: Function that returns a `GegevensdienstNamenlijst <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__

    :type client_info: dict
    :param client_info: Dict containing info about the client application
        (client_id and redirect_url for authorization request responses)

    :type make_request: coroutine
    :param make_request: coroutine that makes a post request. Should have
        the signature :code:`(url:string, body:dict)->dict`. Used to make a authorization exchange
        request to the oauth server.
    """

    def __init__(self, data_store=None, get_zal=None, get_gnl=None, client_info=None, make_request=None):
        assert get_zal is not None, "Can't instantiate Client without 'get_zal'"
        assert get_gnl is not None, "Can't instantiate Client without 'get_gnl'"
        assert make_request is not None, "Can't instantiate Client without 'make_request'"
        assert client_info is not None, "Can't instantiate Client without 'client_info'"

        if not issubclass(data_store.__class__, DataStore):
            raise ValueError(
                'data_store argument should be a subclass of the DataStore abstract class'
            )

        self.data_store = data_store
        self.client_info = client_info
        self.make_request = make_request
        self._get_zal = get_zal
        self._get_gnl = get_gnl

    async def get_zal(self):
        """
            Return a tuple of the ZAL and GNL (zal, gnl) returned by the get_zal and get_gnl
            function supplied in instantiation of Client object
        """
        zal = await self._get_zal()
        gnl = await self._get_gnl()

        return (zal, gnl)

    async def create_oauth_session(self, za_name, gegevensdienst_id, **kwargs):
        """
        Create and return a new OAuthSession to start the oauth flow.
        Add the zorggebruikers choice of zorgaanbieder gegevensdienst. :ref:`(FLOW #2) <flow2>`

        :type za_name: string
        :param za_name: Name of zorgaanbieder chosen by the zorggebruiker.

        :type gegevensdienst_id: string
        :param gegevensdienst_id: Id of the gegevensdienst chosen by the zorggebruiker

        :type \*\*kwargs: various
        :param \*\*kwargs: Keyword arguments get passed on to the data_store.create_oauth_session
            function, e.g. db object

        :return: The created OAuthSession
        :rtype: :ref:`OAuthSession <client.oauthsession>`
        """

        return await self.data_store.create_oauth_session(
            za_name=za_name,
            gegevensdienst_id=gegevensdienst_id,
            scope=gegevensdienst_id,
            state=secrets.token_hex(16),
            **kwargs
        )

    async def create_auth_request_url(self, oauth_session):
        """
        Build and return authorization request url :ref:`(FLOW #2) <flow2>`

        :type oauth_session: :ref:`OAuthSession <client.oauthsession>`
        :param oauth_session: OAuthSession for current zorggebruiker

        :return: The authorization request url
        :rtype: str
        """

        request_dict = {
            'state': oauth_session.state,
            'scope': oauth_session.scope,
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }

        zal, _ = await self.get_zal()
        za = zal[oauth_session.za_name]
        gegevensdienst = za.gegevensdiensten[oauth_session.gegevensdienst_id]
        query_parameters = urllib.parse.urlencode(request_dict)

        return f'{gegevensdienst.authorization_endpoint_uri}?{query_parameters}'

    async def handle_auth_response(self, parameters, **kwargs):
        """
        Handles the response to the authorization request. 
        (:ref:`FLOW #10 <flow10>`, :ref:`FLOW #11 <flow11>`)

        :type parameters: dict
        :param parameters: The query params from the servers's response to the authorization request

        :type \*\*kwargs: various
        :param \*\*kwargs: Keyword arguments get passed on to the data_store.get_oauth_session_by_state
            function, e.g. db object

        :return: The updated OAuthSession no containing the authorization_code, and authorized set to True
        :rtype: :ref:`OAuthSession <client.oauthsession>`

        :raises OAuthException: If validation of the params fails
        :raises ValueError: If there is no session found linked to the state parameter in the provided query parameters
        """
        validation.validate_auth_response(parameters)

        oauth_session = await self.data_store.get_oauth_session_by_state(parameters['state'], **kwargs)

        if oauth_session is None:
            raise ValueError('No oauth_session found!')

        oauth_session.authorization_code = parameters['code']
        oauth_session.authorized = True

        oauth_session = await self.data_store.save_oauth_session(oauth_session, **kwargs)

        return oauth_session

    async def exchange_authorization_code(self, oauth_session, **kwargs):
        """
        Make a request to a oauth server with the supplied make_request function on instantiation of
        the Client, exchange the received authorization code for an access token and update
        the oauth_session. :ref:`(FLOW #12) <flow12>`

        :type oauth_session: :ref:`OAuthSession <client.oauthsession>`
        :param oauth_session: Authorized oauth session of which to exchange the authorization code

        :type \*\*kwargs: various
        :param \*\*kwargs: Keyword arguments get passed on to the data_store.save_oauth_session
            function, e.g. db object

        :return: The updated OAuthSession containing the access_token
        :rtype: :ref:`OAuthSession <client.oauthsession>`

        :raises OAuthException: If the server's response is invalid
        """
        zal, _ = await self.get_zal()
        gegevensdienst = zal[oauth_session.za_name].gegevensdiensten[oauth_session.gegevensdienst_id]

        response = await self.make_request(url=gegevensdienst.token_endpoint_uri, body={
            'grant_type': 'authorization_code',
            'code': oauth_session.authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id
        })

        validation.validate_access_token_response(response, oauth_session)

        oauth_session.access_token = response['access_token']
        oauth_session.authorization_code = None

        oauth_session = await self.data_store.save_oauth_session(oauth_session, **kwargs)

        return oauth_session

    def __repr__(self):
        return f'Client(data_store={repr(self.data_store)}, get_zal={self._get_zal.__name__}, \
            client_info={self.client_info}, make_request={self.make_request.__name__})'

    def __getattr__(self, attr):
        try:
            return self.client_info[attr]
        except AttributeError:
            pass

        raise AttributeError(f'Client has no attribute \'{attr}\'')

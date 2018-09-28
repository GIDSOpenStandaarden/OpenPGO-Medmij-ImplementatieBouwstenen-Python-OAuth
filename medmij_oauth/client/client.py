import urllib.parse

from . import validation

from .data_store import DataStore

class Client:
    """
    Class to assist in the OAuth clientside flow

    :type data_store: `Datastore <medmij_oauth.client.html#datastore>`__
    :param data_store: Must be subclass of DataStore, handles data interaction with
        OAuthSessions see `Datastore <medmij_oauth.client.html#datastore>`__
        for more info.

    :type get_zal: coroutine
    :param get_zal: Function that returns a
        `ZAL <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__

    :type get_whitelist: coroutine
    :param get_whitelist: Function that returns a
        `Whitelist <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__

    :type get_gnl: coroutine
    :param get_gnl: Function that returns a `gnl <#medmij_oauth.client.parse_gnl>`__

    :type client_info: dict
    :param client_info: Dict containing info about the client application
        (client_id and redirect_url for authorization request responses)

    :type make_request: coroutine
    :param make_request: coroutine that makes a post request. Should have
        the signature :code:`(url:string, body:dict)->dict`. Used to make a authorization exchange
        request to the oauth server.
    """

    def __init__(self, data_store=None, get_zal=None, get_gnl=None, get_whitelist=None, client_info=None, make_request=None):
        assert get_zal is not None, "Can't instantiate Client without 'get_zal'"
        assert get_gnl is not None, "Can't instantiate Client without 'get_gnl'"
        assert get_whitelist is not None, "Can't instantiate Client without 'get_whitelist'"
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
        self._get_whitelist = get_whitelist

    async def get_zal(self):
        """
            Return a tuple of the ZAL and GNL returned by the get_zal and get_gnl
            function supplied in instantiation of Client object
        """
        zal = await self._get_zal()
        gnl = await self._get_gnl()

        return (zal, gnl)

    async def create_oauth_session(self, za_name, gegevensdienst_id, **kwargs):
        """
        Create and return a new OAuthSession to start the oauth flow.
        Add the zorggebruikers choice of zorgaanbieder gegevensdienst. `FLOW #2 <welcome.html#id3>`__

        :type za_name: string
        :param za_name: Name of zorgaanbieder chosen by the zorggebruiker.

        :type gegevensdienst_id: string
        :param gegevensdienst_id: Id of the gegevensdienst chosen by the zorggebruiker

        :type \*\*args: various
        :param \*\*args: Keyword arguments get passed on to the data_store.create_oauth_session
            function, e.g. db object

        Returns:
            `OAuthSession <#oauthsession>`__: The created OAuthSession.

        """

        return await self.data_store.create_oauth_session(
            za_name=za_name,
            gegevensdienst_id=gegevensdienst_id,
            **kwargs
        )

    async def create_auth_request_url(self, oauth_session):
        """
        Build and return authorization request url `FLOW #2 <welcome.html#id3>`__

        :type oauth_session: `OAuthSession <#oauthsession>`__
        :param oauth_session: OAuthSession for current zorggebruiker

        Returns:
            request_url: string
        """

        request_dict = {
            'state': oauth_session.state,
            'scope': oauth_session.gegevensdienst_id,
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }

        zal, _ = await self.get_zal()
        za = zal[oauth_session.za_name]
        gegevensdienst = za.gegevensdiensten[oauth_session.gegevensdienst_id]
        query_parameters = urllib.parse.urlencode(request_dict)

        validation.validate_endpoint(
            gegevensdienst.authorization_endpoint_uri,
            await self._get_whitelist()
        )

        return f'{gegevensdienst.authorization_endpoint_uri}?{query_parameters}'

    async def handle_auth_response(self, parameters, **kwargs):
        """
        Handles the response to the authorization request. 
        (`FLOW #10 <welcome.html#id11>`__, `FLOW #11 <welcome.html#id12>`__)

        The response parameters are validated and an appropriate
        `OAuthException <medmij_oauth.exceptions.html#oauthexception>`__ is raised
        if supplied parameters are not valid
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
        the oauth_session. `FLOW #12 <welcome.html#id13>`__

        :type oauth_session: `OAuthSession <#oauthsession>`__
        :param oauth_session: Authorized oauth session of which to exchange the authorization code
        """
        zal, _ = await self.get_zal()
        gegevensdienst = zal[oauth_session.za_name].gegevensdiensten[oauth_session.gegevensdienst_id]

        validation.validate_endpoint(gegevensdienst.token_endpoint_uri, await self._get_whitelist())

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

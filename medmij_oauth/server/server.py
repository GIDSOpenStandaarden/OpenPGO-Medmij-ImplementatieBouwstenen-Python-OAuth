"""Server module to help implementing a oauth server"""
import urllib.parse
import datetime

from medmij_oauth.exceptions import (
    OAuthException,
    ERRORS
)

from . import (
    DataStore,
    tokens,
    validation
)

class Server():
    """
    Class to assist in the OAuth serverside flow

    :type data_store: `Datastore <medmij_oauth.server.html#datastore>`__
    :param data_store: Must be subclass of DataStore, handles data interaction with OAuthSessions see `Datastore <medmij_oauth.server.html#datastore>`__ for more info.

    :type zg_resource_available: function
    :param zg_resource_available: Function that is called by Server.zg_resource_available to determine if resources are available for zorggebruiker.

    :type get_ocl: function
    :param get_ocl: Function that returns a `OCL <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__

    :type get_whitelist: coroutine
    :param get_whitelist: Function that returns a `Whitelist <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__
    """

    def __init__(self, data_store=None, zg_resource_available=None, get_ocl=None, get_whitelist=None):
        assert zg_resource_available is not None, "Can't instantiate Server without 'zg_resource_available'"
        assert get_ocl is not None, "Can't instantiate Server without 'get_ocl'"
        assert get_whitelist is not None, "Can't instantiate Server without 'get_whitelist'"

        if not issubclass(data_store.__class__, DataStore):
            raise ValueError(
                'data_store argument should be a subclass of the DataStore abstract class'
            )

        self.data_store = data_store
        self._get_ocl = get_ocl
        self._get_whitelist = get_whitelist
        self._zg_resource_available = zg_resource_available

    async def get_ocl(self):
        """Return the OCL returned by the get_ocl function supplied in instantiation of Server object"""
        return await self._get_ocl()


    async def create_oauth_session(self, request_parameters, **kwargs):
        """
        Create and return a new `OAuthSession <#oauthsession>`__ request. (`FLOW #3 <index.html#id3>`__)

        request_parameters are validated and an appropriate `OAuthException <medmij_oauth.exceptions.html#oauthexception>`__ is raised if supplied request_parameters are not valid

        :type request_parameters: dict
        :param request_parameters: Dictionary containing the request parameters from the start verzamelen.

        :type \*\*args: various
        :param \*\*args: Keyword arguments get passed on to the data_store.create_oauth_session function, e.g. db object

        Returns:
            OAuthSession: The created `OAuthSession <#oauthsession>`__.

        """
        validation.validate_request_parameters(request_parameters, (await self.get_ocl()), (await self._get_whitelist()))

        oauth_session = await self.data_store.create_oauth_session(
            response_type=request_parameters.get('response_type'),
            client_id=request_parameters.get('client_id'),
            redirect_uri=request_parameters.get('redirect_uri'),
            scope=request_parameters.get('scope'),
            state=request_parameters.get('state'),
            **kwargs
        )

        return oauth_session

    async def zg_resource_available(self, oauth_session=None, oauth_session_id=None, client_data={}, **kwargs):
        """
        Determine if this service has resources available for this zorggebruikers by calling the supplied zg_resource_available function on instatiation of the Server. (`FLOW #8 <index.html#id8>`__)

        This function requires a least an oauth_session or an oauthsession id.
        BSN is added to the client_data that is passed to the self._zg_resource_available function.

        :type oauth_session: `OAuthSession <#oauthsession>`__
        :param oauth_session: OAuthSession for the current zorggebruiker (optional).

        :type oauth_session_id: string
        :param oauth_session_id: ID for the OAuthSession of current zorggebruiker (optional).

        :type client_data: dict
        :param client_data: Optional additional zorggebruikerinfo that gets passed on to the self._zg_resource_available function.

        :type \*\*args: various
        :param \*\*args: Keyword arguments get passed to the supplied self._zg_resource_available function

        Returns:
            bool: returns True if zorggebruiker is known to this service, otherwise a OAuthException is raised

        """
        if oauth_session is None:
            oauth_session = await self.data_store.get_oauth_session_by_id(oauth_session_id)

        _client_data = {
            "bsn": oauth_session.zorggebruiker_bsn,
            **client_data
        }

        resource_available = await self._zg_resource_available(client_data=_client_data, **kwargs)

        if not resource_available:
            raise OAuthException(
                error_code=ERRORS.ACCESS_DENIED,
                error_description='No such resource',
                base_redirect_url=oauth_session.redirect_uri,
                redirect=True
            )

        return True

    async def handle_auth_grant(self, oauth_session_id=None, authorized=False, **kwargs):
        """Handle the zorggebruikers response to the authorization question. (`FLOW #10 <index.html#id10>`__)

        Log whether the zorggebruiker authorized the request.
        If the authorization request is denied an OAuthException is raised.
        If the authorization request is granted a tuple is returned containing the OAuthSession and redirect_url.

        :type oauth_session_id: str
        :param oauth_session_id: ID for the OAuthSession of current zorggebruiker.

        :type authorized: bool
        :param authorized: optional additional zorggebruikerinfo that gets passed on to the self._zg_resource_available function.

        :type \*\*args: various
        :param \*\*args: Keyword arguments get passed on to the various DataStore functions, e.g. db object

        Returns:
            tuple: (OAuthSession, redirect_url)

        """
        oauth_session = await self.data_store.get_oauth_session_by_id(oauth_session_id, **kwargs)

        if oauth_session is None:
            raise ValueError('Not a valid oauth_session_id')

        if not authorized:
            oauth_session.authorization_granted = False

            oauth_session = await self.data_store.save_oauth_session(oauth_session, **kwargs)

            raise OAuthException(
                error_code=ERRORS.ACCESS_DENIED,
                error_description='Authorization denied',
                base_redirect_url=oauth_session.redirect_uri,
                redirect=True
            )

        authorization_code = tokens.create_token()

        oauth_session.authorization_granted = True
        oauth_session.authorization_code = authorization_code.token
        oauth_session.authorization_code_expiration = authorization_code.expiration

        oauth_session = await self.data_store.save_oauth_session(oauth_session, **kwargs)

        return (oauth_session, self.get_authorization_code_redirect_url(oauth_session))

    def get_authorization_code_redirect_url(self, oauth_session):
        """
        Generate a authorization code redirect url for an authorized oauth session.

        :type oauth_session: `OAuthSession <#oauthsession>`__
        :param oauth_session: OAuthSession for which to create the authorization code redirect url.

        Returns:
            str: authorization code redirect url

        """

        if not oauth_session.authorization_granted:
            raise ValueError("Trying to create authorization_code_redirect_url for oauth_session that is not authorized")

        query_dict = {
            'code': oauth_session.authorization_code,
            'state': oauth_session.state,
            'expires_in': (oauth_session.authorization_code_expiration - datetime.datetime.now()).seconds,
            'token_type': 'bearer'
        }

        return f'{oauth_session.redirect_uri}?{urllib.parse.urlencode(query_dict)}'

    async def exchange_authorization_code(self, request_parameters, **kwargs):
        """Handle the oauth client's request to exchange the authorization code for an access token. (`FLOW #13 <index.html#id13>`__)

        Validate the request, update the oauth_session and return dict with response parameters.

        :type request_parameters: str
        :param request_parameters: Params send with the request.

        :type \*\*args: various
        :param \*\*args: Keyword arguments get passed on to the various DataStore functions, e.g. db object

        Returns:
            dict: Dict containing the parameters for a valid response

        """
        oauth_session = await self.data_store.get_oauth_session_by_authorization_code(
            request_parameters.get('code'),
            **kwargs
        )

        validation.validate_exchange_request(request_parameters, oauth_session)

        access_token = tokens.create_token()

        oauth_session.authorization_code = None
        oauth_session.access_token = access_token.token
        oauth_session.access_token_expiration = access_token.expiration

        oauth_session = await self.data_store.save_oauth_session(oauth_session, **kwargs)

        return {
            'access_token': access_token.token,
            'token_type': 'bearer',
            'expires_in': access_token.lifetime.seconds,
            'scope': oauth_session.scope
        }

    def __repr__(self):
        return f'Server(data_store={repr(self.data_store)}, zg_resource_available={self._zg_resource_available.__name__})'

Welcome to MedMij OAuth's documentation
=======================================

The medmij_oauth package assists in implementing an oauth server/client application conform the medmij oauth flow (`described below <#the-medmij-oauth-flow>`__). The module consists of 3 main submodules i.e. `medmij_oauth.server <#server>`__, `medmij_oauth.client <#client>`__ and `medmij_oauth.exceptions <#exceptions>`__ .
The client and server submodules are build for use with an async library like `aiohttp <https://github.com/aio-libs/aiohttp>`__.

Beside the package there are two example implementations available on the `github repo <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python-OAuth>`__, an oauth server and client implementation built using these modules (Only a reference, not for production use!).


Server
======

API Reference: `medmij_oauth.server <medmij_oauth.server.html>`__

The medmij_oauth.server modules goal is to assist in implementing an oauth server, its main component is the Server class.
To make use of the Server class you need to implement the following:

- subclass of DataStore (class)
- OAuthSession (class)
- zg_resource_available (coroutine)
- get_ocl (coroutine)

DataStore ABC (server)
----------------------

Your implementation of the DataStore class handles instantiation, persisting and lookups of OAuthSessions.
The methods that you need to implement can be found on the `DataStore ABC <medmij_oauth.server.html#datastore>`__.

Example implementation:

.. code:: python

    from medmij_oauth.server import (
        DataStore
    )

    import my_oauth_session as OAuthSession

    SESSIONS = {}

    class InMemoryDataStore(DataStore):
        async def create_oauth_session(self, response_type, client_id, redirect_uri, scope, state, **kwargs):
            oauth_session = OAuthSession(
                response_type=response_type,
                client_id=client_id,
                redirect_uri=redirect_uri,
                scope=scope,
                state=state
            )

            SESSIONS[oauth_session.id] = oauth_session

            return oauth_session

        async def get_oauth_session_by_id(self, oauth_session_id, **kwargs):
            return SESSIONS.get(oauth_session_id, None)

        async def get_oauth_session_by_authorization_code(self, authorization_code, **kwargs):
            try:
                oauth_session = [
                    oauth_session for
                    oauth_session in SESSIONS.values()
                    if oauth_session.authorization_code == authorization_code
                ][0]
            except IndexError:
                return None

            return oauth_session

        async def save_oauth_session(self, oauth_session=None, **kwargs):
            return oauth_session

        def __repr__(self):
            return 'InMemoryDataStore()'

Most methods on the Server class use the functions of your implementation of the DataStore to handle interaction with the OAuthSessions.
Any extra keyword arguments given to those functions are passed on to the methods on the DataStore implementation e.g. a DB object of some sort

Example:

.. code:: python

    # In Server Class
    async def create_oauth_session(self, request_parameters, **kwargs):
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

OAuthSession (server)
---------------------

This class represents the state of the current oauth session. The Server class will handle instantiation and interaction with OAuthSessions through your implementation of the DataStore ABC.

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

`more info <medmij_oauth.server.html#oauthsession>`__

zg_resource_available
---------------------

An coroutine that checks if resources are available for the current zorggebruiker, should return a boolean.
Is called when `Server.zg_resource_available <medmij_oauth.server.html#medmij_oauth.server.Server.zg_resource_available>`__ is invoked, with a dict containing at least the BSN of the zorggebruiker.

.. warning:: BSN is added to the OAuthSession in response to the DigiD interaction `FLOW #7 <#id8>`__, this is not (yet) included in the Server class. If you are implementing a server make sure to update the OAuthSession after retreiving the BSN from DigiD.

get_ocl
-------

An coroutine that returns an `OCL <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__.

Example implementation:

.. code:: python

    async def get_ocl():
        # Probably some caching and retreiving an up to date list but as an example load it from disk.
        async with aiofiles.open('path/to/ocl.xml'), mode='r') as file:
            contents = await f.read()
            xml = bytes(file.read(), 'utf-8')

        return medmij_lists.OAuthclientList(xmldata=xml)

get_whitelist
-------------

An coroutine that returns a `Whitelist <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__.

Example implementation:

.. code:: python

    async def get_whitelist():
        # Probably some caching and retreiving an up to date list but as an example load it from disk.
        async with aiofiles.open('path/to/whitelist.xml'), mode='r') as file:
            contents = await f.read()
            xml = bytes(file.read(), 'utf-8')

        return medmij_lists.Whitelist(xmldata=xml)

Server usage example
--------------------

.. code:: python

    from aiohttp import web

    import get_db_somehow

    import my_get_ocl
    import my_datastore_implementation
    import my_zg_resouce_available

    server = Server(
        data_store=my_datastore_implemtation,
        zg_resource_available=my_zg_resouce_available,
        get_ocl=my_get_ocl
    )

    app['server'] = server
    app['db] = get_db_somehow()


    async def get_start_oauth_session(request):
        query_dict = request.query
        server = request.app['server']

        oauth_session = await server.create_oauth_session(query_dict, db=request.app['db'])

        # If there is no resource available the function raises an OAuthException that gets handled by the middleware
        await server.zg_resource_available(oauth_session=oauth_session, client_data={"name": "test patient"})

        ocl = await server.get_ocl()
        pgo = ocl.get(oauth_session.client_id)

        csrf_token = await csrf.generate_csrf_token(request)

        return render_template('ask_auth.html', request, {
            'pgo': pgo,
            'oauth_session_id': oauth_session.id,
            'csrf_token': csrf_token
        })

    app.router.add_get('/oauth/authorize', get_start_session)

    app = web.Application()
    web.run_app(app, port=args.port)

For a full example implementation checkout the `server_implementation <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python-OAuth/tree/master/server_implementation>`__ on github.

Client
======

API Reference: `medmij_oauth.client <medmij_oauth.client.html>`__

The medmij_oauth.client modules goal is to assist in implementing an oauth client, its main component is the Client class.
To make use of the Client class you need to implement/supply the following:

- subclass of DataStore (class)
- OAuthSession (class)
- get_zal (coroutine)
- get_whitelist (coroutine)
- get_gnl (coroutine)
- client_info (dict)
- make_request (coroutine)

DataStore ABC (client)
----------------------

Your implementation of the DataStore class handles instantiation, persisting and lookups of OAuthSessions.
The methods that you need to implement can be found on the `DataStore ABC <medmij_oauth.client.html#datastore>`__.

Example implementation:

.. code:: python

    import secrets
    import uuid

    from ..data_store import (
        DataStore
    )

    import my_oauth_session as OAuthSession

    SESSIONS = {}

    class InMemoryDataStore(DataStore):
        async def create_oauth_session(self, za_name, gegevensdienst_id, **kwargs):
            oauth_session = OAuthSession(
                state=secrets.token_hex(16),
                za_name=za_name,
                gegevensdienst_id=gegevensdienst_id,
                scope=gegevensdienst_id
            )

            SESSIONS[oauth_session.id] = oauth_session

            return oauth_session

        async def get_oauth_session_by_id(self, oauth_session_id, **kwargs):
            return SESSIONS.get(oauth_session_id, None)

        async def get_oauth_session_by_state(self, state, **kwargs):
            try:
                oauth_session = [
                    oauth_session for
                    oauth_session in SESSIONS.values()
                    if oauth_session.state == state
                ][0]
            except IndexError:
                return None

            return oauth_session

        async def save_oauth_session(self, oauth_session=None, **kwargs):
            return oauth_session

        def __repr__(self):
            return 'InMemoryDataStore()'

Most methods on the Client class use the functions of your implementation of the DataStore to handle interaction with the OAuthSessions.
Any extra keyword arguments given to those functions are passed on to the methods on the DataStore implementation e.g. a DB object of some sort.

Example:

.. code:: python

    #In Client class
    async def create_oauth_session(self, za_name, gegevensdienst_id, **kwargs):
        return await self.data_store.create_oauth_session(
            za_name=za_name,
            gegevensdienst_id=gegevensdienst_id,
            **kwargs
        )

OAuthSession (client)
---------------------

This class represents the state of the current oauth session. The Server class will handle instantiation and interaction with OAuthSessions through your implementation of the DataStore ABC.

Example implementation:

.. code:: python

    class OAuthSession():
        def __init__(self, state, za_name, gegevensdienst_id, scope):
            self.id = str(uuid.uuid4())
            self.state = state
            self.scope = gegevensdienst_id
            self.za_name = za_name
            self.gegevensdienst_id = gegevensdienst_id
            self.authorization_code = None
            self.authorized = False
            self.access_token = None

`more info <medmij_oauth.client.html#oauthsession>`__

get_zal
-------

An coroutine that returns a `ZAL <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__.

Example implementation:

.. code:: python

    async def get_zal():
        # Probably some caching and retreiving an up to date list but as an example load it from disk.
        async with aiofiles.open('path/to/zal.xml'), mode='r') as file:
            contents = await f.read()
            xml = bytes(file.read(), 'utf-8')

        return medmij_lists.ZAL(xmldata=xml)

get_whitelist
-------------

An coroutine that returns a `Whitelist <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__.

Example implementation:

.. code:: python

    async def get_whitelist():
        # Probably some caching and retreiving an up to date list but as an example load it from disk.
        async with aiofiles.open('path/to/whitelist.xml'), mode='r') as file:
            contents = await f.read()
            xml = bytes(file.read(), 'utf-8')

        return medmij_lists.Whitelist(xmldata=xml)



get_gnl
-------

An coroutine that returns a `GNL <https://afsprakenstelsel.medmij.nl/display/PUBLIC/Processen+en+informatie>`__. The supplied `parse_gnl <medmij_oauth.client.html#medmij_oauth.client.parse_gnl>`__ function can be used to parse the Gegevensdienstnamenlijst xml.

Example implementation:

.. code:: python

    async def get_test_gnl():
        # Probably some caching and retreiving an up to date list but as an example load it from disk.

        gnl = parse_gnl(ET.parse(
           'path/to/MedMij_Gegevensdienstnamenlijst_example.xml'
        ).getroot())

        return gnl


client_info
-----------

Dict containing info about the client application e.i. client_id and redirect_url for authorization request responses.

Example:

.. code:: python

    client_info = {
        "client_id": "oauthclient.local",
        "redirect_url": "https://oauthclient.local/oauth/cb"
    }

make_request
------------------------

Coroutine that makes a POST request. Should have the signature (url: string, body: dict) -> dict .
Used by the client to make a `exchange_authorization_code <medmij_oauth.client.html#medmij_oauth.client.Client.exchange_authorization_code>`__ request to the oauth server.

Example:

.. code::

    # Example uses aiohttp client (https://docs.aiohttp.org/en/stable/client.html) to make the actual request.
    # For a complete example of how to implement this check out the example client implementation.

    async def make_request(self, url='', body=None):
        optional_data = {}

        if body is not None:
            if not isinstance(body, str):
                body = json.dumps(body)

            optional_data['data'] = body.encode('utf-8')

        async with self.session.request("POST", url, **optional_data) as resp:
            json_resp = await resp.json()

        return json_resp

Client usage example
--------------------

.. code:: python

    from aiohttp import web

    import get_db_somehow

    import my_datastore_implementation
    import my_get_zal
    import my_get_whitelist
    import my_get_gnl
    import my_make_request

    client_info = {
        "client_id": "oauthclient.local",
        "redirect_url": "https://oauthclient.local/oauth/cb"
    }

    client = Client(
        data_store=my_datastore_implemtation,
        get_zal=my_get_zal,
        get_whitelist=my_get_whitelist,
        get_gnl=my_get_gnl,
        make_request=my_make_request,
        client_info=client_info
    )

    app['client'] = client
    app['db] = get_db_somehow()

    async def get_start_session(request):
        client = request.app['client']
        client = request.app['db']

        session = await create_oauth_session(request_params, db=db)

    app.router.add_get('/oauth/start', get_start_session)

    app = web.Application()
    web.run_app(app, port=args.port)

For a full example implementation checkout the `client_implementation <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python-OAuth/tree/master/client_implementation>`__ on github.

Exceptions
==========

API Reference: `medmij_oauth.exceptions <medmij_oauth.exceptions.html>`__

The OAuthException class is used to represent an error as described in `rfc6749 <https://tools.ietf.org/html/rfc6749>`__.
The exception contains the error, error_description, if it is allowed to redirect, redirect_url if allowed and correct HTTP status_code.

The different possible errors are contained in the `ERRORS enum <medmij_oauth.exceptions.html#medmij_oauth.exceptions.ERRORS>`__. Further optional arguments that the OAuthException's constructor takes are, *error_descripion*, *redirect* and *redirect_url*.

Example Usage:

.. code:: python

    raise OAuthException(ERRORS.INVALID_REQUEST, error_description='Invalid redirect url', redirect=False)

.. code:: python

    raise OAuthException(ERRORS.UNAUTHORIZED_CLIENT, error_description='No such resource', redirect=True, base_redirect_url='https://oauthclient.com')

Example of OAuth exception handling in middleware

.. code:: python

    ...

    async def oauth_error_middleware(request, handler):
        try:
            response = await handler(request)
            return response
        except OAuthException as ex:
            # If redirect is set on the exception, it is safe to redirect zorggebruiker to supplied redirect url
            if ex.redirect:
                return web.HTTPFound(ex.get_redirect_url())

            # Else just render to screen with the correct HTTP statuscode
            return web.Response(
                text=ex.get_json(),
                status=ex.status_code,
                content_type='application/json'
            )


The MedMij OAuth flow
=====================

In the API references you find links to this flow, that means that those functions assist in implementing this step of the oauth flow. (e.g. `Server.create_oauth_session <medmij_oauth.server.html#medmij_oauth.server.Server.create_oauth_session>`__)

.. _1:

1. De PGO Server start de flow door in de PGO Presenter van de Zorggebruiker de mogelijkheid te presenteren om een bepaalde Gegevensdienst bij een zekere Zorgaanbieder te verzamelen. Het gaat altijd om precies één Gegevensdienst (één scope, in OAuth-termen). Uit de Zorgaanbiederslijst weet de PGO Server welke Gegevensdiensten voor een Zorgaanbieder beschikbaar zijn. Desgewenst worden de Gegevensdienstnamen uit de Gegevensdienstnamenlijst gebruikt.

.. _2:

2. De Zorggebruiker maakt expliciet zijn selectie en laat de OAuth User Agent een verzamel-verzoek sturen naar de Authorization Server. Het adres van het authorization endpoint komt uit de ZAL. De redirect URI geeft aan waarnaartoe de Authorization Server de OAuth User Agent verderop moet redirecten (met de authorization code).

.. _3:

3. Daarop begint de Authorization Server de OAuth-flow (in zijn rol als OAuth Authorization Server) door een sessie te creëren.

.. _4:

4. Dan start de Authorization Server (nu in de rol van SAML Service Provider) de SAML-flow door de browser naar DigiD te redirecten, onder meegeven van een redirect URI, die aangeeft waarnaartoe DigiD straks de OAuth User Agent moet terugsturen, na het inloggen van de Zorggebruiker.

.. _5:

5. DigiD vraagt van de Zorggebruiker via zijn PGO Presenter om inloggegevens.

.. _6:

6. Wanneer deze juist zijn, redirect DigiD de OAuth User Agent terug naar de Authorization Server, onder meegeven van een ophaalbewijs: het SAML-artefact.

.. _7:

7. Met dit ophaalbewijs haalt de Authorization Server rechtstreeks bij DigiD het BSN op.

.. _8:

8. De Authorization Server controleert alvast of de Zorgaanbieder voor de betreffende Gegevensdienst überhaupt gezondheidsinformatie van die Persoon beschikbaar heeft. Daarvan maakt deel uit dat de Persoon daarvoor minstens 16 jaar oud moet zijn.

.. _9:

9. Zo ja, dan presenteert de Authorization Server via de PGO Presenter aan Zorggebruiker de vraag of laatstgenoemde hem toestaat de gevraagde persoonlijke gezondheidsinformatie aan de PGO Server (als OAuth Client) te sturen. Onder het flow-diagram staat gespecificeerd welke informatie, waarvandaan, de OAuth Authorization Server verwerkt in de aan Zorggebruiker voor te leggen autorisatievraag.

.. _10:

10. Bij akkoord logt de Authorization Server dit als toestemming, genereert een authorization code en stuurt dit als ophaalbewijs, door middel van een browser redirect met de in stap 1 ontvangen redirect URI, naar de PGO Server. De Authorization Server stuurt daarbij de local state-informatie mee die hij in de eerste stap van de PGO Server heeft gekregen. Laatstgenoemde herkent daaraan het verzoek waarmee hij de authorization code moet associëren.

.. _11:

11. De PGO Server vat niet alleen deze authorization code op als ophaalbewijs, maar leidt er ook uit af dat de toestemming is gegeven en logt het verkrijgen van het ophaalbewijs.

.. _12:

12. Met dit ophaalbewijs wendt de PGO Server zich weer tot de Authorization Server, maar nu zonder tussenkomst van de OAuth User Agent, voor een access token.

.. _13:

13. Daarop genereert de Authorization Server een access token en stuurt deze naar de PGO Server.

.. _14:

14. Nu is de PGO Server gereed om het verzoek om de gezondheidsinformatie naar de Resource Server te sturen. Het adres van het resource endpoint haalt hij uit de ZAL. Hij plaatst het access token in het bericht en zorgt ervoor dat in het bericht geen BSN is opgenomen.

.. _15:

15. De Resource Server controleert of het ontvangen token recht geeft op de gevraagde resources, haalt deze (al dan niet) bij achterliggende bronnen op en verstuurt ze in een FHIR-response naar de PGO Server.

.. _16:

16. Deze bewaart de ontvangen gezondheidsinformatie in het persoonlijke dossier. Mocht de  Gegevensdienst  waartoe de  Zorggebruiker  heeft geautoriseerd uit meerdere  Transacties  bestaan, bevraagt de  PGO Server  de  Resource Server  daarna mogelijk opnieuw voor de nog resterende  Transacties , eventueel na nieuwe gebruikersinteractie. Zolang het access token geldig is, kan dat.

.. include:: tests.rst

.. include:: requirements.rst
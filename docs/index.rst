.. MedMijOAuth documentation master file, created by
   sphinx-quickstart on Sun Sep 23 21:22:28 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MedMij OAuth's documentation!
=======================================

The medmij_oauth package assists in implementing an oauth server/client application conform the medmij oauth flow (described below), it consists of 3 modules (server, client and exceptions).
The client and server modules are build for use with an async library like `aiohttp <https://github.com/aio-libs/aiohttp>`__.

Beside the package there are two example implementations available on the `github repo <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python-OAuth>`__, an oauth server and client implementation built using these modules.

Modules
-------

Server
~~~~~~

API Reference: `medmij_oauth.server <medmij_oauth.server.html>`__

The medmij_oauth.server modules goal is to assist in implementing an oauth server, its main component is the Server class.
To make use of the Server class you need to implement the following:

- subclass of DataStore (class)
- OAuthSession (class)
- zg_resource_available (coroutine)
- get_ocl (coroutine)

**DataStore ABC**

Your implementation of the DataStore class handles instantiation, persisting and lookups of OAuthSessions.
The methods that you need to implement can be found on the `DataStore ABC <medmij_oauth.server.html#DataStore>`__.
Most methods on the Server class use the functions of your implementation of the DataStore.
Any extra keyword arguments given to those functions are passed on to the methods on the DataStore implementation.

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

`more info <medmij_oauth.server.html#DataStore>`__

**OAuthSession**

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

**zg_resource_available**

An coroutine that checks if resources are available for the current zorggebruiker. Should return a boolean and is called by the Server object with a dict containing at least the BSN of the zorggebruiker.

`more info <medmij_oauth.server.Server.zg_resource_available>`__

**get_ocl**

An coroutine that returns an OCL object.

Example implementation:

.. code:: python

    async def get_ocl():
        async with aiofiles.open(path.join(path.dirname(__file__), 'resources/ocl.xml'), mode='r') as file:
            contents = await f.read()
            xml = bytes(file.read(), 'utf-8')

        return medmij_lists.OAuthclientList(xmldata=xml)

`more info <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python>`__


Server usage example
````````````````````

.. code:: python

    from aiohttp import web

    import my_get_ocl
    import my_datastore_implemtation
    import my_zg_resouce_available

    server = Server(
        data_store=my_datastore_implemtation,
        zg_resource_available=my_zg_resouce_available,
        get_ocl=my_get_ocl
    )

    app['server'] = server
    app['db] = get_db_somehow()

    async def get_start_session(request):
        server = request.app['server']
        server = request.app['db']

        session = await create_oauth_session(request_params, db=db)

    app.router.add_get('/oauth/start', get_start_session)

    app = web.Application()
    web.run_app(app, port=args.port)

For a full example implementation checkout the `server_implementation <https://github.com/GidsOpenStandaarden/OpenPGO-Medmij-ImplementatieBouwstenen-Python-OAuth/tree/master/server_implementation>`__ on github.

Client
~~~~~~

API Reference: `medmij_oauth.client <medmij_oauth.client.html>`__

Exceptions
~~~~~~~~~~

API Reference: `medmij_oauth.exceptions <medmij_oauth.exceptions.html>`__

The MedMij OAuth flow
---------------------

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

Requirements
------------

Modules
~~~~~~~
- Python >=3.6

Example implementations
~~~~~~~~~~~~~~~~~~~~~~~
- aiohttp==3.3.2
- aiohttp-jinja2==1.0.0
- aiohttp-session==2.5.1
- cryptography==2.3
- SQLAlchemy==1.2.10

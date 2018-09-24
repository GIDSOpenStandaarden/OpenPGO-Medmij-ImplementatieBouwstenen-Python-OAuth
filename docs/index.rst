.. MedMijOAuth documentation master file, created by
   sphinx-quickstart on Sun Sep 23 21:22:28 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MedMijOAuth's documentation!
=======================================

The medmij_oauth package assist in implementing an oauth server/client application conform the medmij oauth flow (described below), it consists of 3 modules (server, client and exceptions).
The client and server modules are made for an async implementation.

Beside the package there are two example implementations available on the github repo, an oauth server and client implementation built using these modules.

Modules
-------

Server
~~~~~~

Reference documentation: `medmij_oauth.server <medmij_oauth.server.html>`__

The medmij_oauth.server modules goal is to assist in implementing an oauth server conform the medmij flow, its main component is the Server class.

To make use of the Server class you need to implement the following:

- subclass of DataStore (class)
- OAuthSession (class)
- zg_resource_available (async function)
- get_ocl (async function)

**Subclass of DataStore**

Your implementation of the DataStore class handles interaction with the OAuthSession class and persisting it (e.g. store the oauth session to a database)

`more info <medmij_oauth.server.html#DataStore>`__

**OAuthSession**

This class represents the state of the current oauth session. The Server class will handle instantiation and interaction with OAuthSessions through your implementation of the DataStore ABC.

`more info <medmij_oauth.server.html#oauthsession>`__

**zg_resource_available**

An async function that checks if resources are available for the current oauth_session. This function should return a boolean and is called by the Server object with a dict containing at least the BSN of the zorggebruiker.

`more info <medmij_oauth.server.Server.zg_resource_available>`__

**get_ocl**

An async function that returns an OCL object.

`more info <medmij_oauth.server.html#ocl-oauth-client-lijst>`__


On instatiation the Server class it needs 3 arguments

- data_store
- zg_resource_available
- get_ocl

The data_store argument is implementation of the `DataStore <medmij_oauth.server.html#datastore>`__ Baseclass


Client
~~~~~~

`medmij_oauth.client <medmij_oauth.client.html>`__

Exceptions
~~~~~~~~~~

`medmij_oauth.exceptions <medmij_oauth.exceptions.html>`__

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

class Systeemrol:
    def __init__(self, ss_dict):
        self.resource_endpoint = ss_dict['resource_endpoint']
        self.systeemrolcode = ss_dict['systeemrolcode']

    __slots__ = ('resource_endpoint', 'systeemrolcode')

    def __repr__(self):
        return f'<Systeemrol: systeemrolcode={self.systeemrolcode}, resource_endpoint={self.resource_endpoint}>'

class Gegevensdienst:
    """
    Python object that represents a Gegevensdienst

    :type gegevensdienst_dict: dict
    :param gegevensdienst_dict: Dict with information of gegevensdienst.

    :type parent_name: string
    :param parent_name: Name of zorgaanbieder where this gegevensdienst belongs to.

    :type gnl: dict
    :param gnl: dict containing gegevensdienstnamen supplied by the medmij_oauth.client.parse_gnl function.
    """
    def __init__(self, gegevensdienst_dict, gnl, parent_name='Onbekend'):
        self._parent_name = parent_name
        self.id = gegevensdienst_dict['id']
        self.token_endpoints = gegevensdienst_dict['token_endpoints']
        self.authorization_endpoints = gegevensdienst_dict['authorization_endpoints']
        self.systeemrollen = [Systeemrol(systeemrol) for systeemrol in gegevensdienst_dict['systeemrollen']]
        self.display_name = gnl[gegevensdienst_dict['id']]

    @property
    def token_endpoint(self):
        """ Return the first token endpoint of this gegevensdienst"""
        return self.token_endpoints[0]

    @property
    def authorization_endpoint(self):
        """ Return the first authorization endpoint of this gegevensdienst"""
        return self.authorization_endpoints[0]

    def endpoints(self):
        """ Return generator that itterates over all endpoint couples (self.authorization_endpoints[i], self.token_endpoints[i])"""
        return ((self.authorization_endpoints[i], self.token_endpoints[i]) for i in range(len(self.token_endpoints)))

    __slots__ = ('_parent_name', 'id', 'token_endpoints', 'authorization_endpoints', 'systeemrollen', 'display_name')

    def __repr__(self):
        return f'<Gegevensdient: {self.id} ({self._parent_name})>'

class Zorgaanbieder:
    """
    Python object that represents a Zorgaanbieder

    :type zal_list: list
    :param zal_list: List containing dicts with zorgaanbieder information

    :type gnl: dict
    :param gnl: dict containing gegevensdienstnamen supplied by the medmij_oauth.client.parse_gnl functio
    """
    def __init__(self, za_dict, gnl):
        self.naam = za_dict['naam']
        self.gegevensdiensten = {gegevensdient['id']:Gegevensdienst(gegevensdient, gnl, parent_name=self.naam) for gegevensdient in za_dict['gegevensdiensten']}

    __slots__ = ('naam', 'gegevensdiensten', 'gnl')

    def __repr__(self):
        return f'<Zorgaanbieder: {self.naam}>'

class ZAL:
    """
    Python object that represents a ZAL (`Zorgaanbiederslijst <https://afsprakenstelsel.medmij.nl/display/PUBLIC/XML-schema%27s?preview=/22348206/22348210/MedMij_Zorgaanbiederslijst.xsd>`__)

    Don't instantiate this class manually, use `parse_zal <#medmij_oauth.client.parse_zal>`__ instead

    :type zal_list: list
    :param zal_list: List containing dicts with za information

    :type gnl: dict
    :param gnl: dict containing gegevensdienstnamen supplied by the medmij_oauth.client.parse_gnl function
    """
    _zorgaanbieders = {}

    def __init__(self, zal_list, gnl):
        self._zorgaanbieders = dict((zorgaanbieder["naam"], Zorgaanbieder(zorgaanbieder, gnl)) for zorgaanbieder in zal_list)
        self.gnl = gnl
    def list_zal_names(self):
        """
            Get a list of zorgaanbieder names.
        """
        return list(self._zorgaanbieders.keys())

    def items(self):
        """
            Get a list of all zorgaanbieders in ZAL.
        """
        return self._zorgaanbieders.items()

    def __getitem__(self, item):
        try:
            return self._zorgaanbieders[item]
        except KeyError:
            raise KeyError(f'No resource available with name \'{item}\'')

    def __iter__(self):
        for za in self._zorgaanbieders.values():
          yield za

    def __repr__(self):
        return f'<ZAL ({len(self._zorgaanbieders)} zorgaanbieders>)'

VERSION = 'release2'

class XMLIdentifiers:
    ZORGAANBIEDER = f'{{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/{VERSION}/}}Zorgaanbieder'
    ZORGAANBIEDER_NAAM = f'{{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/{VERSION}/}}Zorgaanbiedernaam'
    GEGEVENSDIENSTEN = f'{{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/{VERSION}/}}Gegevensdiensten'
    GEGEVENSDIENST_ID = f'{{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/{VERSION}/}}GegevensdienstId'
    SYSTEEMROLLEN = f'{{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/{VERSION}/}}Systeemrollen'
    RESOURCE_ENDPOINT = f'{{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/{VERSION}/}}ResourceEndpoint'
    SYSTEEMROLCODE = f'{{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/{VERSION}/}}Systeemrolcode'
    TOKEN_ENDPOINT = f'{{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/{VERSION}/}}TokenEndpoint'
    AUTH_ENDPOINT = f'{{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/{VERSION}/}}AuthorizationEndpoint'

def parse_zal(zal, gnl):
    """
        Convert a xml.etree.ElementTree.ElementTree into a `ZAL <#medmij_oauth.client.ZAL>`__ Object

        :type zal: xml.etree.ElementTree.ElementTree
        :param zal: a xml.etree.ElementTree.ElementTree containing the ZAL

        :type gnl: dict
        :param gnl: dict containing gegevensdienstnamen supplied by the medmij_oauth.client.parse_gnl function

        Return:
            `ZAL <#medmij_oauth.client.ZAL>`__ object with data from the ETree object
    """
    zorgaanbieders = []

    for zorgaanbieder in zal.iter(XMLIdentifiers.ZORGAANBIEDER):
        zorgaanbieder_dict = {}
        zorgaanbieder_dict['naam'] = zorgaanbieder.find(XMLIdentifiers.ZORGAANBIEDER_NAAM).text
        zorgaanbieder_dict['gegevensdiensten'] = []

        for gegevensdienst in zorgaanbieder.find(XMLIdentifiers.GEGEVENSDIENSTEN):
            gegevensdienst_dict = {
                'id': gegevensdienst.find(XMLIdentifiers.GEGEVENSDIENST_ID).text,
                'token_endpoints': [],
                'authorization_endpoints': [],
                'systeemrollen': []
            }

            for systeemrol in gegevensdienst.find(XMLIdentifiers.SYSTEEMROLLEN):
                gegevensdienst_dict['systeemrollen'].append({
                    'resource_endpoint': systeemrol.find(XMLIdentifiers.RESOURCE_ENDPOINT).text,
                    'systeemrolcode': systeemrol.find(XMLIdentifiers.SYSTEEMROLCODE).text
                })

            gegevensdienst_dict['token_endpoints'] += [endpoint.text for endpoint in gegevensdienst.find(XMLIdentifiers.TOKEN_ENDPOINT)]
            gegevensdienst_dict['authorization_endpoints'] += [endpoint.text for endpoint in gegevensdienst.find(XMLIdentifiers.AUTH_ENDPOINT)]

            zorgaanbieder_dict['gegevensdiensten'].append(gegevensdienst_dict)

        zorgaanbieders.append(zorgaanbieder_dict)

    return ZAL(zorgaanbieders, gnl)

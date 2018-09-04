class Systeemrol:
    def __init__(self, ss_dict):
        self.resource_endpoint = ss_dict['resource_endpoint']
        self.systeemrolcode = ss_dict['systeemrolcode']

    __slots__ = ('resource_endpoint', 'systeemrolcode')

    def __repr__(self):
        return f'<Systeemrol: systeemrolcode={self.systeemrolcode}, resource_endpoint={self.resource_endpoint}>'

class Gegevensdienst:
    def __init__(self, gd_dict, parent_name='Onbekend'):
        self._parent_name = parent_name
        self.id = gd_dict['id']
        self.token_endpoints = gd_dict['token_endpoints']
        self.authorization_endpoints = gd_dict['authorization_endpoints']
        self.systeemrollen = [Systeemrol(systeemrol) for systeemrol in gd_dict['systeemrollen']]

    @property
    def token_endpoint(self):
        return self.token_endpoints[0]

    @property
    def authorization_endpoint(self):
        return self.authorization_endpoints[0]

    __slots__ = ('_parent_name', 'id', 'token_endpoints', 'authorization_endpoints', 'systeemrollen')

    def __repr__(self):
        return f'<Gegevensdient: {self.id} ({self._parent_name})>'

class Zorgaanbieder:
    def __init__(self, za_dict):
        self.naam = za_dict['naam']
        self.gegevensdiensten = [Gegevensdienst(gegevensdient, self.naam) for gegevensdient in za_dict['gegevensdiensten']]

    __slots__ = ('naam', 'gegevensdiensten')

    @property
    def token_endpoint(self):
        return self.gegevensdiensten[0].token_endpoint

    @property
    def authorization_endpoint(self):
        return self.gegevensdiensten[0].authorization_endpoint

    def __repr__(self):
        return f'<Zorgaanbieder: {self.naam}>'

class ZAL:
    _zorgaanbieders = {}

    def __init__(self, zal_dict):
        self._zorgaanbieders = dict((zorgaanbieder["naam"], Zorgaanbieder(zorgaanbieder)) for zorgaanbieder in zal_dict)

    def list_zal_names(self):
        return list(self._zorgaanbieders.keys())

    def items(self):
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

class XMLIdentifiers:
    ZORGAANBIEDER = '{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/release2/}Zorgaanbieder'
    ZORGAANBIEDER_NAAM = '{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/release2/}Zorgaanbiedernaam'
    GEGEVENSDIENSTEN = '{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/release2/}Gegevensdiensten'
    GEGEVENSDIENST_ID = '{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/release2/}GegevensdienstId'
    SYSTEEMROLLEN = '{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/release2/}Systeemrollen'
    RESOURCE_ENDPOINT = '{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/release2/}ResourceEndpoint'
    SYSTEEMROLCODE = '{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/release2/}Systeemrolcode'
    TOKEN_ENDPOINT = '{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/release2/}TokenEndpoint'
    AUTH_ENDPOINT = '{xmlns://afsprakenstelsel.medmij.nl/zorgaanbiederslijst/release2/}AuthorizationEndpoint'

def parse_zal(zal):
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

    return ZAL(zorgaanbieders)
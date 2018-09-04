class OCL:
    _clients = {}

    def __init__(self, ocl_list):
        self._clients = dict((client["hostname"], client) for client in ocl_list)

    def list_hostnames(self):
        return list(self._clients.keys())

    def items(self):
        return self._clients.items()

    def get(self, key):
        return self._clients.get(key)

    def __getitem__(self, item):
        try:
            return self._clients[item]
        except KeyError:
            raise KeyError(f'No resource available with name \'{item}\'')

    def __iter__(self):
        for za in self._clients.values():
            yield za

    def __repr__(self):
        return f'<ZAL ({len(self._clients)} clients>)'

class XMLIdentifiers:
    OAUTHCLIENTS = '{xmlns://afsprakenstelsel.medmij.nl/oauthclientlist/release2/}OAuthclients'
    HOSTNAME = '{xmlns://afsprakenstelsel.medmij.nl/oauthclientlist/release2/}Hostname'
    ORGANIZATION_NAME = '{xmlns://afsprakenstelsel.medmij.nl/oauthclientlist/release2/}OAuthclientOrganisatienaam'

def parse_ocl(ocl):
    clients = []

    for client in ocl.find(XMLIdentifiers.OAUTHCLIENTS):
        client_dict = {
            'hostname': client.find(XMLIdentifiers.HOSTNAME).text,
            'organization_name': client.find(XMLIdentifiers.ORGANIZATION_NAME).text
        }

        clients.append(client_dict)

    return OCL(clients)

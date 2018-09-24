
class OCL:
    """
    Python object that represents a OCL (`MedMij OAuth Client List <https://afsprakenstelsel.medmij.nl/download/attachments/22348206/MedMij_OAuthclientlist.xsd?version=1&modificationDate=1535034702931&api=v2>`__)

    Don't instantiate this class manually, use `parse_ocl <#medmij_oauth.server.parse_ocl>`__ instead

    :type ocl_list: list
    :param ocl_list: List containing dicts with client information
    """

    def __init__(self, ocl_list):
        self._clients = dict((client["hostname"], client) for client in ocl_list)

    _clients = {}


    def list_hostnames(self):
        """Return a list of client hostnames"""
        return list(self._clients.keys())

    def items(self):
        """Return a list of clients"""
        return self._clients.items()

    def get(self, key):
        """
        Return a client based on its hostname

        :type key: string
        :param key: hostname of a client
        """
        return self._clients.get(key)

    def __getitem__(self, item):
        try:
            return self.get(item)
        except KeyError:
            raise KeyError(f'No resource available with name \'{item}\'')

    def __iter__(self):
        for za in self._clients.values():
            yield za

    def __repr__(self):
        return f'<OCL ({len(self._clients)} clients>)'

VERSION = 'release2'

class XMLIdentifiers:
    OAUTHCLIENTS = f'{{xmlns://afsprakenstelsel.medmij.nl/oauthclientlist/{VERSION}/}}OAuthclients'
    HOSTNAME = f'{{xmlns://afsprakenstelsel.medmij.nl/oauthclientlist/{VERSION}/}}Hostname'
    ORGANIZATION_NAME = f'{{xmlns://afsprakenstelsel.medmij.nl/oauthclientlist/{VERSION}/}}OAuthclientOrganisatienaam'

def parse_ocl(ocl):
    """
        Converts a xml.etree.ElementTree.ElementTree into a `OCL <#medmij_oauth.server.OCL>`__ Object

        :type ocl: xml.etree.ElementTree.ElementTree
        :param ocl: a xml.etree.ElementTree.ElementTree containing the OCL

        Return:
            OCL object with data from the ETree object
    """
    clients = []

    for client in ocl.find(XMLIdentifiers.OAUTHCLIENTS):
        client_dict = {
            'hostname': client.find(XMLIdentifiers.HOSTNAME).text,
            'organization_name': client.find(XMLIdentifiers.ORGANIZATION_NAME).text
        }

        clients.append(client_dict)

    return OCL(clients)

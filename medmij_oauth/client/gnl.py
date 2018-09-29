VERSION = 'release1'

class XMLIdentifiers:
    GEGEVENSDIENSTEN = f'{{xmlns://afsprakenstelsel.medmij.nl/gegevensdienstnamenlijst/{VERSION}/}}Gegevensdiensten'
    GEGEVENSDIENST = f'{{xmlns://afsprakenstelsel.medmij.nl/gegevensdienstnamenlijst/{VERSION}/}}Gegevensdienst'
    GEGEVENSDIENST_ID = f'{{xmlns://afsprakenstelsel.medmij.nl/gegevensdienstnamenlijst/{VERSION}/}}GegevensdienstId'
    WEERGAVENAAM = f'{{xmlns://afsprakenstelsel.medmij.nl/gegevensdienstnamenlijst/{VERSION}/}}Weergavenaam'

def parse_gnl(gnl):
    """
        Convert a xml.etree.ElementTree.ElementTree into a dict containing the gnl

        :type gnl: xml.etree.ElementTree.ElementTree
        :param gnl: a xml.etree.ElementTree.ElementTree containing the gnl

        :return: gnl with data from the ETree object
        :rtype: dict
    """
    gnl_dict = {}

    for gegevensdienst in gnl.find(XMLIdentifiers.GEGEVENSDIENSTEN):
        gnl_dict[gegevensdienst.find(XMLIdentifiers.GEGEVENSDIENST_ID).text] = gegevensdienst.find(XMLIdentifiers.WEERGAVENAAM).text

    return gnl_dict

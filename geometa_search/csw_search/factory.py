from owslib.csw import CatalogueServiceWeb
from csw_search_service import CSWSearchService


def create_service(config_path):
    csw = CatalogueServiceWeb('http://www.geocat.ch/geonetwork/srv/de/csw')
    return CSWSearchService(csw)

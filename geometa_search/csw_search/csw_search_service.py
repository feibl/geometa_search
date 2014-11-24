from ..search_service import SearchService
from ..search_service import Record

from owslib.fes import PropertyIsEqualTo


class CSWSearchService(SearchService):
    """
    Implementation of the Search Service using CSW
    """

    def __init__(self, csw):
        self.csw = csw

    def search_by_keyword(
            self, query_string, start_position=0, max_records=10):
        query = PropertyIsEqualTo('csw:AnyText', query_string)

        self.csw.getrecords2(
            constraints=[query],
            startposition=start_position,
            maxrecords=max_records,
            esn='summary',
            resulttype='results')

        num_matches = self.csw.results['matches']

        search_results = []
        for record in self.csw.records:
            search_result = Record(record)
            search_results.append(search_result)

        return search_results, num_matches

    def search_by_ids(self, record_ids):
        self.csw.getrecordbyid(
            id=record_ids, esn='full')

        search_results = {}
        for record_id, record in self.csw.records.iteritems():
            search_results[record_id] = Record(record)

        return search_results

    def search_by_id(self, record_id):
        self.csw.getrecordbyid(
            id=[record_id], esn='full')

        return Record(self.csw.records[record_id])

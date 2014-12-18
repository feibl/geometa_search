from ..search_service import SearchService
from ..search_service import Record

from owslib.fes import PropertyIsEqualTo
from owslib.ows import ExceptionReport


class CSWSearchService(SearchService):
    """
    Implementation of the Search Service using CSW
    """

    def __init__(self, csw):
        self.csw = csw

    def search_by_keywords(
            self, query_string, start_position=0, max_records=10):
        query = PropertyIsEqualTo('csw:AnyText', query_string)

        self.csw.getrecords2(
            constraints=[query],
            startposition=start_position,
            maxrecords=max_records,
            esn='summary',
            resulttype='results')

        num_matches = self.csw.results['matches']

        print('{} matches'.format(num_matches))
        print('{}'.format(self.csw.records.keys()))

        search_results = []
        for record_id, record in self.csw.records.iteritems():
            search_result = Record(record)
            search_results.append(search_result)

        return search_results, num_matches

    def search_by_ids(self, record_ids):
        try:
            self.csw.getrecordbyid(
                id=record_ids, esn='full')

            search_results = {}
            for record_id, record in self.csw.records.iteritems():
                search_results[record_id] = Record(record)
                print('Record: {}'.format(record_id))

            return search_results

        except ExceptionReport:
            print('Get Records by ids could not be evaluated')

        return {}

    def search_by_id(self, record_id):
        records = self.search_by_ids([record_id])
        if record_id in records:
            return Record(records[record_id])
        return None

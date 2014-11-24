class Record(object):

    def __init__(self, csw_record):
        self.__dict__ = csw_record.__dict__
        if csw_record.abstract is not None:
            self.snippet = csw_record.abstract[:200]
        else:
            self.snippet = ''


class SearchService(object):
    """
    Declares functions used for searching records
    """

    def search_by_keywords(
            self, query_string, start_position=0, max_records=10):
        """
        Searches records matching the given keywords.

        :param query_string: the query
        :param start_position: starting index in the result list
        :param max_records: maximum numbers of records returned
        """
        raise NotImplementedError()

    def search_by_ids(self, record_ids):
        """
        Searches records by ids

        :param record_ids: list of ids of the requested records
        """
        raise NotImplementedError()

    def search_by_id(self, record_id):
        """
        Searches a single record having the specified id

        :param record_id: id of the requested record
        """
        raise NotImplementedError()

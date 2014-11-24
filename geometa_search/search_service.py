class SearchService(object):
    """
    Declares functions used for searching records
    """

    def search_by_keyword(query_string, start_index=0, how_many=10):
        """
        Searches records matching the given keywords.

        :param query_string: the query
        :param start_index: starting index in the result list
        :param how_many: maximum numbers of records returned
        """
        raise NotImplementedError()

    def search_by_id(record_id):
        """
        Searches a record having the specified id

        :param record_id: id of the record
        """
        raise NotImplementedError()

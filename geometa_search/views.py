from .services import searcher
from core import InvalidUsage

from flask import Blueprint
from flask import render_template
from flask import request
from flask import abort
from flask import session
from flask import current_app
from flask import jsonify

import requests

from math import ceil
import uuid
import M2Crypto
from time import time
from datetime import datetime

from collections import OrderedDict

import logging


logger = logging.getLogger(__name__)


meta_search = Blueprint('meta_search', __name__)


rec_sys_address = 'http://localhost:5000/recommender/api'
RESULTS_PER_PAGE = 10


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
                    (
                        num > self.page - left_current - 1 and
                        num < self.page + right_current
                    ) or \
                    num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def parse_arg(
        request, arg_name, default_value=None, type=None, required=False):
    try:
        arg = request.args[arg_name]
        if type is not None:
            arg = type(arg)
    except KeyError:
        if required:
            raise InvalidUsage(
                u'Missing required parameter {}'.format(arg_name),
                status_code=400)
        arg = default_value
    except ValueError:
        if required:
            raise InvalidUsage(
                u'Parameter {} could not be parsed'.format(arg_name),
                status_code=400)
        arg = default_value

    return arg


class SearchResult(object):

    def __init__(self, record_id, title, abstract):
        self.identifier = record_id
        self.title = title
        self.abstract = abstract
        self.snippet = abstract[:100]
        self.recommendation = None

    def is_recommended(self):
        return self.recommendation is not None


class Recommendation(object):

    def __init__(self, last_interaction, total_hits):
        self.last_interaction = last_interaction
        self.total_hits = total_hits


def deserialize_recommendation(json_rec):
    return Recommendation(
        last_interaction=json_rec['last_interaction'],
        total_hits=json_rec['total_hits'])


def create_search_result(record):
    return SearchResult(
        record.identifier, record.title, record.abstract)


def create_session_id():
    return uuid.UUID(bytes=M2Crypto.m2.rand_bytes(16))


def generate_query_id(query):
    return str(hash('{}{}{}'.format('salt', query, str(int(time())))))


def get_search_recommendations(
        query_string, include_internal_records, num_promotions=3):
    promoted_results = []
    recommendations = OrderedDict()

    payload = {
        'query_string': query_string,
        'include_internal_records': include_internal_records,
        'api_key': current_app.config['API_KEY'],
    }
    r = requests.get(
        rec_sys_address + '/recommended_search_results',
        params=payload
    )

    try:
        r_json = r.json()
        for json_rec in r_json['results']:
            recommendations[json_rec['record_id']] =\
                deserialize_recommendation(json_rec)

        print('Num recommended records {}'.format(len(recommendations)))

        promotions = []
        promotion_ids = []
        for i in range(min(num_promotions, len(recommendations))):
            promoted_id, promotion = recommendations.popitem(last=False)
            promotions.append(promotion)
            promotion_ids.append(promoted_id)

        print('Promotions {}'.format(promotion_ids))

        if len(promotion_ids) > 0:
            records = searcher.search_by_ids(promotion_ids)
            print('Found promotions {}'.format(len(records)))
            found_records = []
            for p_id in promotion_ids:
                if p_id in records:
                    found_records.append(records[p_id])

            for record in found_records:
                promotion = promotions[promotion_ids.index(record.identifier)]
                search_result = create_search_result(record)
                search_result.recommendation = promotion
                promoted_results.append(search_result)
        else:
            print('No recommendations'.format())

    except ValueError:
        print('No JSON object could be decoded')

    return promoted_results, recommendations


def report_view(is_internal_record, session_id, record_id, query_string=None):
    payload = {
        'is_internal_record': is_internal_record,
        'record_id': record_id,
        'api_key': current_app.config['API_KEY'],
        'session_id': session_id,
        'timestamp': datetime.utcnow().isoformat()
    }
    if query_string:
        payload['query_string'] = query_string
    requests.get(
        rec_sys_address + '/view',
        params=payload
    )


def get_similar_queries(query_string, max_results=3):
    payload = {
        'query_string': query_string,
        'api_key': current_app.config['API_KEY'],
    }
    print(payload)
    r = requests.get(
        rec_sys_address + '/similar_queries',
        params=payload
    )
    print(r.text)

    sim_queries = []
    try:
        r_json = r.json()
        sim_queries = r_json['results']
    except ValueError:
        print('No JSON object could be decoded')

    return sim_queries[:max_results]


@meta_search.before_request
def before_request():
    if 'session_id' not in session:
        session_id = create_session_id()
        session['session_id'] = session_id
        logger.info('New session created: %s', session_id)


@meta_search.route('/')
def index():
    '''
    Start page with search form
    '''
    return render_template('layout.html')


@meta_search.route('/search')
def search():
    '''
    Returns search-results from records matching a
    search-text to the client
    '''
    query = parse_arg(request, 'q', required=True)
    page = parse_arg(
        request, 'page', required=False, type=int, default_value=1)

    logging.info('Search Request received. Query: %s', query)

    sim_queries = get_similar_queries(query)

    records, num_matches = searcher.search_by_keywords(
        query, (page - 1) * RESULTS_PER_PAGE, RESULTS_PER_PAGE)

    results = [create_search_result(record) for record in records]

    # Add recommended search result if on first page
    if not page or page == 1:
        promotions, remaining_recs = get_search_recommendations(
            query, True)

        # Delete search results from normal search list if promoted
        promoted_ids = [p.identifier for p in promotions]

        merged_results = promotions

        for i, result in enumerate(results):
            if result.identifier in promoted_ids:
                continue
            if result.identifier in remaining_recs:
                result.recommendation = remaining_recs[result.identifier]
            merged_results.append(result)

        results = merged_results

    return render_template(
        'meta_search/search_results.html',
        query=query,
        results=results,
        sim_queries=sim_queries,
        num_matches=num_matches,
        pagination=Pagination(page, RESULTS_PER_PAGE, num_matches))

    return render_template('layout.html')


@meta_search.route('/show')
def show():
    '''
    Shows the metadata with the given id
    '''
    query = parse_arg(request, 'q', required=False)
    record_id = parse_arg(request, 'record_id', required=True)

    logger.info(
        'Show request received. Record: %s, Query: %s', record_id, query)

    record = searcher.search_by_id(record_id)

    if record is None:
        abort(404)

    # Report a view request
    if query is not None:
        report_view(True, session['session_id'], record_id, query)
        return render_template(
            'meta_search/show.html', query=query,
            record=record)
    else:
        report_view(True, session['session_id'], record_id)
        return render_template(
            'meta_search/show.html', record=record)


@meta_search.route('/other_users_also_used')
def other_users_also_used():
    payload = {
        'session_id': session['session_id'],
        'api_key': current_app.config['API_KEY'],
        'include_internal_records': True,
        'max_num_recs': 5,
    }
    r = requests.get(
        rec_sys_address + '/other_users_also_used',
        params=payload
    )
    recommendations = []
    try:
        r_json = r.json()
        print(r_json)
        recommended_records = []
        for json_rec in r_json['results']:
            recommended_records.append(json_rec['record_id'])

        if len(recommended_records) > 0:
            for record_id in recommended_records:
                record = searcher.search_by_id(record_id)
                if record:
                    recommendations.append({
                        'identifier': record.identifier,
                        'title': record.title,
                    })
        else:
            print('No recommendations'.format())

    except ValueError:
        print('No JSON object could be decoded')

    return jsonify(results=recommendations)


@meta_search.route('/create_new_session')
def create_new_session():
    print('New Session ID')
    logger.info('New session id requested')
    session_id = create_session_id()
    session['session_id'] = session_id

    logger.info('New session created: %s', session_id)

    return render_template('layout.html')


@meta_search.route('/influenced_by_your_history')
def influenced_by_your_history():
    payload = {
        'session_id': session['session_id'],
        'api_key': current_app.config['API_KEY'],
        'include_internal_records': True,
        'max_num_recs': 5,
    }
    r = requests.get(
        rec_sys_address + '/influenced_by_your_history',
        params=payload
    )
    recommendations = []
    try:
        r_json = r.json()
        print(r_json)
        recommended_records = []
        for json_rec in r_json['results']:
            recommended_records.append(json_rec['record_id'])

        if len(recommended_records) > 0:
            for record_id in recommended_records:
                record = searcher.search_by_id(record_id)
                if record:
                    recommendations.append({
                        'identifier': record.identifier,
                        'title': record.title,
                    })
        else:
            print('No recommendations'.format())

    except ValueError:
        print('No JSON object could be decoded')

    return jsonify(results=recommendations)


@meta_search.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    abort(404)


@meta_search.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

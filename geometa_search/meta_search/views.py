from ..services import searcher

from flask import Blueprint
from flask import render_template
from flask import request
from flask import abort
from flask import session

import requests

import uuid
import M2Crypto
from time import time

from collections import OrderedDict


meta_search = Blueprint('meta_search', __name__)


rec_sys_address = 'http://localhost:5000/recommender/api'


sessions = {}


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


@meta_search.before_request
def before_request():
    if 'session_id' not in session:
        session_id = create_session_id()
        session['session_id'] = session_id
        sessions[session_id] = set()
    elif session['session_id'] not in sessions:
        sessions[session['session_id']] = set()


def generate_query_id(query):
    return str(hash('{}{}{}'.format('salt', query, str(int(time())))))


def get_recommendations(query_string, community_id, num_promotions=3):
    promoted_results = []
    recommendations = OrderedDict()

    payload = {
        'query_string': query_string,
        'community_id': community_id,
        'api_key': str(1234),
    }
    r = requests.get(
        rec_sys_address + '/recommend',
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


def register_hit(query_string, community_id, session_id, record_id):
    payload = {
        'query_string': query_string,
        'community_id': community_id,
        'record_id': record_id,
        'api_key': str(1234),
        'session_id': session_id,
        'timestamp': int(time())
    }
    print(int(time()))
    print(payload)
    r = requests.get(
        rec_sys_address + '/view',
        params=payload
    )
    print(r.text)


def get_similar_queries(query_string, community_id, max_results=3):
    payload = {
        'query_string': query_string,
        'community_id': community_id,
        'api_key': str(1234),
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
    query = request.args['q']
    community_id = request.args['cid']

    if query and community_id:
        sim_queries = get_similar_queries(query, community_id)
        promotions, remaining_recs = get_recommendations(query, community_id)

        query_id = generate_query_id(query)
        sessions[session['session_id']].update([query_id])
        print(sessions[session['session_id']])

        records, num_matches = searcher.search_by_keywords(query)

        results = promotions
        promoted_ids = [p.identifier for p in promotions]
        for record in records:
            if record.identifier in promoted_ids:
                continue
            search_result = create_search_result(record)
            if record.identifier in remaining_recs:
                search_result.recommendation =\
                    remaining_recs[record.identifier]
            results.append(search_result)

        return render_template(
            'meta_search/search_results.html', query=query,
            query_id=query_id, results=results,
            sim_queries=sim_queries,
            num_matches=num_matches)

    return render_template('layout.html')


@meta_search.route('/show')
def show():
    '''
    Shows the metadata with the given id
    '''
    record_id = request.args.get('record_id')
    query = request.args['q']
    community_id = request.args['cid']
    query_id = request.args['qid']
    print(query_id)

    if record_id and query and community_id and query_id:
        print(sessions[session['session_id']])
        if query_id in sessions[session['session_id']]:
            print('register hit')
            register_hit(query, community_id, session['session_id'], record_id)

        record = searcher.search_by_id(record_id)
        if record:
            return render_template(
                'meta_search/show.html', query=query,
                record=record)

    abort(404)

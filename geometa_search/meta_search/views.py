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


meta_search = Blueprint('meta_search', __name__)


rec_sys_address = 'http://localhost:5000/recommender/api'


sessions = {}


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


def get_recommendations(query_string, community_id):
    recs = []

    payload = {
        'query_string': query_string,
        'community_id': community_id,
        'api_key': str(1234),
    }
    print(payload)
    r = requests.get(
        rec_sys_address + '/recommend',
        params=payload
    )
    print(r.text)

    try:
        r_json = r.json()
        record_ids = []
        for rec in r_json['results']:
            record_ids.append(rec['record_id'])

        if len(record_ids) > 0:
            print('Recommendations: {}'.format(record_ids))
            records = searcher.search_by_ids(record_ids)
            for record_id in record_ids:
                if record_id in records:
                    recs.append(records[record_id])
        else:
            print('No recommendations'.format())

    except ValueError:
        print('No JSON object could be decoded')

    return recs


def register_hit(query_string, community_id, session_id, record_id):
    # TODO: address as variable
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


def get_similar_queries(query_string, community_id):
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

    return sim_queries


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
        recs = get_recommendations(query, community_id)

        query_id = generate_query_id(query)
        sessions[session['session_id']].update([query_id])
        print(sessions[session['session_id']])

        records, num_matches = searcher.search_by_keywords(query)

        return render_template(
            'meta_search/search_results.html', query=query,
            query_id=query_id, results=records,
            sim_queries=sim_queries, recommendations=recs,
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

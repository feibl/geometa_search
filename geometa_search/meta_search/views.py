from flask import Blueprint
from flask import render_template
from flask import request


meta_search = Blueprint('meta_search', __name__)


class SearchResult(object):
    def __init__(self, title, record_id, snippet):
        self.title = title
        self.record_id = record_id
        self.snippet = snippet


results = [
    SearchResult(
        'Ali Baba',
        '1ab3',
        'This is the story about Ali Baba and friends'
    ),
    SearchResult(
        'Aladin',
        '3g68',
        'Aladin wears pants that look like a pyjama'
    )
]


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
    return render_template(
        'meta_search/search_results.html', query=query,
        results=results)


@meta_search.route('/show')
def show():
    '''
    Shows the metadata with the given id
    '''
    record_id = request.args.get('record_id')

    return 'You view {}'.format(
        record_id)

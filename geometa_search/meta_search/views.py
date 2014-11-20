from flask import Blueprint, render_template, request


meta_search = Blueprint('meta_search', __name__)


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
    return 'You searched with query: {}'.format(request.args.get('q'))


@meta_search.route('/show')
def show():
    '''
    Shows the metadata with the given id
    '''
    metadataid = request.args.get('id')
    query_string = request.args.get('q')

    return 'You view have clicked on {} after query {}'.format(
        record_id, query_string)

# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import httplib
from urllib import urlencode, quote


view_action = 'view'
copy_action = 'copy'

session_alice = 'alice'
session_bob = 'bob'
session_carol = 'carol'
session_dave = 'dave'
session_eric = 'eric'
session_fred = 'frank'
session_garry = 'garry'
session_hally = 'hally'
session_ian = 'ian'
session_jenny = 'jenny'

query_plan = 'zug plan'
query_erdwarme = 'zug erdwärme'
query_zone = 'zug zone'
query_zug = 'zug'
query_zivilschutz = 'zug zivilschutz'
query_gefahr = 'zug gefahren'
query_energie = 'zug energie'
query_militar = 'zug militär'
query_solar = 'zug solarenergie'

record_zonenplan = '8200c268-a01f-48fe-96c6-ce1cd14b38da'
record_solarkataster = '9e4099e6-09ca-4498-b694-5a39849b7fa9'
record_erderwarmung = '8a4271bf-b5eb-4c3f-8b81-c72d39ac650f'
record_bauplan = '46cf3140-c92a-4188-9931-e7d6ed828440'
record_gefahr = '498033f5-dd11-497c-bbb2-34fab58a1fa6'
record_unbebaut = 'f0277c25-f137-4225-8607-ab756d7fe828'
record_schutzraum = 'c0ec1e7d-505e-4d20-a076-d8698a45a9f7'

date_group1 = datetime.utcnow() - timedelta(6 * 30)
date_group2 = datetime.utcnow()

actions = [
    (session_alice, query_plan, view_action, record_zonenplan, date_group1),
    (session_alice, query_erdwarme, copy_action, record_erderwarmung, date_group1),
    (session_alice, query_zone, view_action, record_gefahr, date_group1),
    (session_alice, query_zivilschutz, copy_action, record_schutzraum, date_group1),

    (session_bob, query_erdwarme, copy_action, record_erderwarmung, date_group1),
    (session_bob, query_zone, view_action, record_unbebaut, date_group1),
    (session_bob, query_zivilschutz, copy_action, record_schutzraum, date_group1),

    (session_carol, query_energie, copy_action, record_erderwarmung, date_group1),
    (session_carol, query_gefahr, view_action, record_gefahr, date_group1),
    (session_carol, query_zone, copy_action, record_unbebaut, date_group1),

    (session_dave, query_energie, view_action, record_erderwarmung, date_group1),
    (session_dave, query_militar, copy_action, record_schutzraum, date_group1),

    (session_eric, query_zug, view_action, record_zonenplan, date_group1),
    (session_eric, query_zug, copy_action, record_erderwarmung, date_group1),
    (session_eric, query_zug, view_action, record_schutzraum, date_group1),

    (session_fred, query_erdwarme, copy_action, record_erderwarmung, date_group1),
    (session_fred, query_plan, view_action, record_unbebaut, date_group1),
    (session_fred, query_zivilschutz, copy_action, record_schutzraum, date_group1),

    (session_garry, query_plan, copy_action, record_zonenplan, date_group2),
    (session_garry, query_solar, copy_action, record_solarkataster, date_group2),
    (session_garry, query_erdwarme, view_action, record_erderwarmung, date_group2),
    (session_garry, query_plan, view_action, record_bauplan, date_group2),

    (session_hally, query_energie, copy_action, record_solarkataster, date_group2),
    (session_hally, query_energie, copy_action, record_erderwarmung, date_group2),
    (session_hally, query_zug, copy_action, record_bauplan, date_group2),
    (session_hally, query_gefahr, view_action, record_gefahr, date_group2),

    (session_ian, query_erdwarme, copy_action, record_erderwarmung, date_group2),
    (session_ian, query_gefahr, view_action, record_gefahr, date_group2),

    (session_jenny, query_energie, copy_action, record_solarkataster, date_group2),
    (session_jenny, query_energie, copy_action, record_erderwarmung, date_group2),
    (session_jenny, query_plan, view_action, record_bauplan, date_group2),
]


from geometa_search.factory import create_app as create_frontend
from search_rex.factory import create_app as create_backend
from search_rex.recommendations import create_recommender_system
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple


class Config(object):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI =\
        'postgresql://postgres:postgres@localhost/test_rex'
    API_KEY = 'a18cccd4ff6cd3a54a73529e2145fd36'
    SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    SERVER_NAME = 'localhost:5000'


def import_demo_data():
    api_key = Config.API_KEY

    conn = httplib.HTTPConnection('localhost', 5000)

    for (s, q, a, r, ts) in actions:
        params = urlencode({
            'api_key': api_key,
            'is_internal_record': False,
            'query_string': q,
            'session_id': s,
            'record_id': r,
            'timestamp': ts.isoformat(),
        })
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        if a == view_action:
            conn.request("GET", '/recommender/api/view?' + params, headers=headers)
        else:
            conn.request("GET", '/recommender/api/copy?' + params, headers=headers)

        response = conn.getresponse()
        responseString = response.read()
        print responseString


if __name__ == '__main__':
    config = Config()

    backend = create_backend(config)

    with backend.app_context():
        print('Dropping tables')
        from search_rex.core import db
        db.drop_all()
        db.create_all()

    from search_rex.recommendations.refreshable import Refreshable
    from search_rex.recommendations.refreshable import RefreshHelper
    import search_rex.recommendations.data_model.item_based as item_based_dm
    import search_rex.recommendations.data_model.case_based as case_based_dm
    import search_rex.recommendations.recommenders.item_based as item_based_rec
    import search_rex.recommendations.recommenders.case_based as query_based_rec
    import search_rex.recommendations.similarity.item_based as item_based_sim
    import search_rex.recommendations.similarity.case_based as query_based_sim
    from search_rex.recommendations.similarity.similarity_metrics import jaccard_sim
    import search_rex.recommendations.neighbourhood.item_based as item_based_nhood
    import search_rex.recommendations.neighbourhood.case_based as query_based_nhood

    class ItemSim(item_based_sim.CosineSimilarity):
        def __init__(self):
            super(ItemSim, self).__init__()

        def get_similarity(self, from_prefs, to_prefs):
            sim = super(ItemSim, self).get_similarity(
                from_prefs, to_prefs)
            print(
                'Similarity: {} {}: {}'.format(
                    {sess: pref.value for sess, pref in
                        from_prefs.iteritems()},
                    {sess: pref.value for sess, pref in
                        to_prefs.iteritems()}, sim))
            return sim

    class RecordSim(item_based_sim.RecordSimilarity):
        def __init__(self, data_model, sim_metric):
            super(RecordSim, self).__init__(data_model, sim_metric)

        def get_similarity(self, from_id, to_id):
            sim = super(RecordSim, self).get_similarity(
                from_id, to_id)
            print(
                'Similarity: {} {}: {}'.format(
                    from_id, to_id, sim))
            return sim

    def r_based_recsys_factory(include_internal_records):
        data_model = item_based_dm.PersistentRecordDataModel(
            include_internal_records)

        in_mem_dm = item_based_dm.InMemoryRecordDataModel(data_model)
        content_sim = item_based_sim.InMemoryRecordSimilarity(
            include_internal_records)
        sim_metric = item_based_sim.CosineSimilarity()
        # sim_metric = ItemSim()
        sim_metric = item_based_sim.TimeDecaySimilarity(sim_metric)
        collaborative_sim = item_based_sim.RecordSimilarity(
             in_mem_dm, sim_metric)
        # collaborative_sim = RecordSim(
        #     in_mem_dm, sim_metric)
        combined_sim = item_based_sim.CombinedRecordSimilarity(
            collaborative_sim, content_sim, weight=0.75)

        nhood = item_based_nhood.KNearestRecordNeighbourhood(
            10, in_mem_dm, combined_sim)

        return item_based_rec.RecordBasedRecommender(
            data_model, record_nhood=nhood, record_sim=combined_sim)

    class QuerySim(query_based_sim.AbstractQuerySimilarity):

        def __init__(self):
            self.ngram_sim = query_based_sim.StringJaccardSimilarity(3)

        def get_similarity(self, from_query_string, to_query_string):
            sim1 = self.ngram_sim.get_similarity(
                from_query_string, to_query_string)
            sim2 = jaccard_sim(
                from_query_string.split(), to_query_string.split())
            return max(sim1, sim2)

        def refresh(self, refreshed_components):
            refreshed_components.add(self)

    def q_based_recsys_factory(include_internal_records):
        data_model = case_based_dm.PersistentQueryDataModel(
            include_internal_records, perform_time_decay=False)

        in_mem_dm = case_based_dm.InMemoryQueryDataModel(data_model)
        sim = QuerySim()
        nhood = query_based_nhood.ThresholdQueryNeighbourhood(
            in_mem_dm, sim, sim_threshold=0.25)
        scorer = query_based_rec.WeightedSumScorer(
            query_based_rec.LogFrequency(base=2))

        return query_based_rec.QueryBasedRecommender(
            in_mem_dm, nhood, sim, scorer)

    create_recommender_system(
        backend, r_based_recsys_factory, q_based_recsys_factory)
    frontend = create_frontend(config)
    app = DispatcherMiddleware(
        frontend, {
            '/recommender': backend
        }
    )

    run_simple(
        'localhost', 5000, app, use_reloader=True,
        use_debugger=True, threaded=True)



from flask.ext.restful import Resource

from webservices import utils
from webservices import filters
from webservices.common import counts
from webservices.common import models
from webservices.config import SQL_CONFIG


class ItemizedResource(Resource):

    model = None
    year_column = None
    index_column = None
    filter_multi_fields = []
    filter_fulltext_fields = []

    def get(self, **kwargs):
        query = self.build_query(kwargs)
        count = counts.count_estimate(query, models.db.session, threshold=5000)
        return utils.fetch_seek_page(query, kwargs, self.index_column, count=count)

    def build_query(self, kwargs):
        query = self.model.query.filter(
            self.year_column >= SQL_CONFIG['START_YEAR_ITEMIZED'],
        )

        query = filters.filter_multi(query, kwargs, self.filter_multi_fields)
        query = filters.filter_range(query, kwargs, self.filter_range_fields)
        query = self.filter_fulltext(query, kwargs)

        return query

    def filter_fulltext(self, query, kwargs):
        if any(kwargs[key] for key, column in self.filter_fulltext_fields):
            query = self.join_fulltext(query)
        for key, column in self.filter_fulltext_fields:
            if kwargs[key]:
                query = utils.search_text(query, column, kwargs[key], order=False)
        return query

"""
Custom pagination classes for the API.

StandardPagination is the default — used by most endpoints.
LargePagination is for endpoints where the client typically
wants all records (skills, categories).
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Standard paginator: 12 items per page.
    Supports ?page_size= override up to a max of 50.
    """
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'count':     self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'next':      self.get_next_link(),
                'previous':  self.get_previous_link(),
            },
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'pagination': {
                    'type': 'object',
                    'properties': {
                        'count':        {'type': 'integer'},
                        'total_pages':  {'type': 'integer'},
                        'current_page': {'type': 'integer'},
                        'next':         {'type': 'string', 'nullable': True},
                        'previous':     {'type': 'string', 'nullable': True},
                    }
                },
                'results': schema,
            }
        }


class LargePagination(PageNumberPagination):
    """
    Used for endpoints where the client typically needs all records
    in one go — skills, categories, etc.
    """
    page_size = 100
    max_page_size = 200
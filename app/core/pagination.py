from collections import OrderedDict
from math import ceil

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPager(PageNumberPagination):
    page_size_query_param = "page_size"

    def pages_count(self):
        return ceil(self.page.paginator.count / self.get_page_size(self.request))

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("current", self.page.number),
                    ("pages_count", self.pages_count()),
                    ("page_size", self.get_page_size(self.request)),
                    ("page_size_query_param", self.page_size_query_param),
                    ("page_query_param", self.page_query_param),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 123,
                },
                "next": {
                    "type": "string",
                    "nullable": True,
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                },
                "current": {
                    "type": "integer",
                    "nullable": True,
                },
                "results": schema,
            },
        }

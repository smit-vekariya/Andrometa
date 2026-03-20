from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework import filters
from rest_framework.permissions import DjangoModelPermissions
from manager.base_serializer import DefaultSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class SetPagination(PageNumberPagination):
    page = 1
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "page": int(self.request.GET.get("page", 1)),
                "page_size": int(self.request.GET.get("page_size", self.page_size)),
                "data": data,
                "message": "success",
                "status": 1,
            }
        )


class BaseModelViewSet(ModelViewSet):
    queryset = None
    serializer_class = DefaultSerializer
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    pagination_class = SetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    parser_classes = (FormParser, MultiPartParser, JSONParser)
    search_fields = []
    ordering_fields = ()

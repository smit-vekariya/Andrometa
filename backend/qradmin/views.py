from django.shortcuts import render
from account.serializers import BondUserListSerializers
from account.models import BondUser
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django.template.loader import render_to_string
from manager.manager import HttpsAppResponse


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param= "page_size"
    max_page_size = 1000

class UserList(generics.ListAPIView):
    queryset = BondUser.objects.filter(is_deleted=False)
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    serializer_class = BondUserListSerializers
    search_fields =["first_name", "email"]
    pagination_class = CustomPagination

class DashBoardView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            total_bond_user = BondUser.objects.filter(is_deleted=False).count()
            return HttpsAppResponse.send([{"total_bond_user":total_bond_user}], 1, "Data fetch successfully")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))
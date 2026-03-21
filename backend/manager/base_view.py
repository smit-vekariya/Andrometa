from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework import filters
from rest_framework.permissions import DjangoModelPermissions
from manager.base_serializer import DefaultSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from manager.manager import HttpsAppResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from manager.manager import custom_response_errors



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
    permission_classes = (IsAuthenticated,)
    pagination_class = SetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    parser_classes = (FormParser, MultiPartParser, JSONParser)
    search_fields = []
    ordering_fields = ()


    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and self.queryset is not None:
            return self.queryset.filter(user=user, is_deleted=False)
        return self.queryset

    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            serializer = self.serializer_class(instance=obj)
            return HttpsAppResponse.send(serializer.data, 1, "Success", status_code=status.HTTP_200_OK)
        except Exception as e:
            return HttpsAppResponse.exception(str(e), status_code=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()

            # search & ordering
            search_param = request.GET.get("search")
            ordering_param = request.GET.get("ordering")
            if search_param or ordering_param:
                queryset = self.filter_queryset(queryset)

            # custom filters
            filters_param = request.GET.get("filters")
            if filters_param:
                try:
                    filters = json.loads(filters_param)
                    queryset = self.apply_filters(queryset, filters)
                except json.JSONDecodeError as e:
                    return HttpsAppResponse.send([], 0, f"Invalid filters: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)

            page = self.paginate_queryset(queryset)
            serializer_class = self.get_serializer_class()

            if page is not None:
                serializer = serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = serializer_class(queryset, many=True)
            return HttpsAppResponse.send(
                serializer.data, 1,
                "No data found." if not serializer.data else "Success",
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return HttpsAppResponse.exception(str(e))

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data,
                context={"created_by": request.user, "user": request.user},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return HttpsAppResponse.send(serializer.data, 1, "Success", status_code=status.HTTP_201_CREATED)
        except ValidationError as ve:
            formatted_errors = custom_response_errors(responses=ve.detail)
            if (
                isinstance(formatted_errors, list)
                and len(formatted_errors) == 1
                and isinstance(formatted_errors[0], dict)
                and "non_field_errors" in formatted_errors[0]
            ):
                formatted_errors = formatted_errors[0]["non_field_errors"]

            return HttpsAppResponse.send([], 0, formatted_errors, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return HttpsAppResponse.exception(str(e), status_code=status.HTTP_400_BAD_REQUEST)


    def update(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            serializer = self.serializer_class(
                instance=obj,
                data=request.data,
                context={"updated_by": request.user, "user": request.user},
                partial=True,
            )
            if serializer.is_valid():
                serializer.save()
                return HttpsAppResponse.send(serializer.data, 1, "Success", status_code=status.HTTP_200_OK)
            else:
                formatted_errors = custom_response_errors(responses=serializer.errors)
                if (
                    isinstance(formatted_errors, list)
                    and len(formatted_errors) == 1
                    and isinstance(formatted_errors[0], dict)
                    and "non_field_errors" in formatted_errors[0]
                ):
                    formatted_errors = formatted_errors[0]["non_field_errors"]
                return HttpsAppResponse.send([], 0, formatted_errors, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return HttpsAppResponse.exception(str(e), status_code=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            obj.soft_delete(user=request.user)
            return HttpsAppResponse.send([], 1, "Deleted Successfully.", status_code=status.HTTP_200_OK)
        except Exception as e:
            return HttpsAppResponse.exception(str(e), status_code=status.HTTP_400_BAD_REQUEST)
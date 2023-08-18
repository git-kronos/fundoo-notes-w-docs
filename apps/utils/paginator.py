from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from rest_framework.pagination import PageNumberPagination


def paginate_obj(object_list, request, obj_per_page=5):
    p = Paginator(object_list, obj_per_page)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get("page")
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)

    return page_obj


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 20


def paginate_api_response(request, qs, SerializerKlass):
    paginator = StandardPagination()
    result_page = paginator.paginate_queryset(qs, request)
    serializer = SerializerKlass(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

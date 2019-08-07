from rest_framework import pagination

class WsPagination(pagination.LimitOffsetPagination):
    PAGE_SIZE = 1

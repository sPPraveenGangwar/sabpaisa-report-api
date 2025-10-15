"""
Custom pagination classes for optimized large dataset handling
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# Global setting for maximum page size across all APIs
MAX_PAGE_SIZE = 10000


class CustomPostPagination(PageNumberPagination):
    """
    Memory-efficient pagination for large datasets
    Optimized for handling 10M+ transaction records
    Used by: Transaction History, Settlement History, Refund History
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE  # Set to 10000 for all APIs
    page_query_param = 'page'

    def get_paginated_response(self, data):
        # Return count for all pages (needed for frontend pagination)
        try:
            count = self.page.paginator.count
            total_pages = self.page.paginator.num_pages
        except (AttributeError, ValueError, TypeError):
            count = None
            total_pages = None

        return Response({
            'count': count,
            'total_pages': total_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page.paginator.per_page,
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for very large result sets (reports, exports)
    Used by: Analytics, Reports, Exports
    """
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE  # Set to 10000 for all APIs

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'total_count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': self.page.paginator.per_page,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            },
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'results': data
        })
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):
    # 默认的 page size，也就是 page 没有在 url 参数里的时候
    page_size = 20
    # 默认的 page_size_query_param 是 None 表示不允许客户端指定每一页的大小
    # 如果加上这个配置，就表示客户端可以通过 size=10 来指定一个特定的大小用于不同的场景
    # 比如手机端和web端访问同一个API但是需要的 size 大小是不同的。
    page_size_query_param = 'size'
    # 允许客户端指定的最大 page_size 是多少
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })

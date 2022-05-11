from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 自定义 queryset，因为 newsfeed 的查看是有权限的
        # 只能看 user=当前登录用户的 newsfeed
        # 也可以是 self.request.user.newsfeed_set.all()
        # 但是一般最好还是按照 NewsFeed.objects.filter 的方式写，更清晰直观
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        serializer = NewsFeedSerializer(
            self.get_queryset(),
            context={'request': request},
            many=True,
        )
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)

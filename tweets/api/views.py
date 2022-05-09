from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializerForList, TweetSerializerForCreate
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService


class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list tweets
    """
    # self.get_queryset() will execute the queryset ORM;
    # queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        """
        Assign permission requirement for each method
        """
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """
        重载 list 方法，不列出所有 tweets，必须要求指定 user_id 作为筛选条件
        """
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)

        # 这句查询会被翻译为
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # 这句 SQL 查询会用到 user 和 created_at 的联合索引
        # 单纯的 user 索引是不够的

        # improvement 1: prefetch_related, get rid of N + 1 queries problem
        # improvement 2: cache
        tweets = Tweet.objects.filter(user_id=request.query_params['user_id'])\
            .prefetch_related('user')\
            .order_by('-created_at')
        serializer = TweetSerializerForList(tweets, many=True)
        # 一般来说 json 格式的 response 默认都要用 hash 的格式
        # 而不能用 list 的格式（约定俗成）
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        重载 create 方法，因为需要默认用当前登录用户作为 tweet.user
        """
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        # save will trigger create method in TweetserializerForCreate
        tweet = serializer.save()
        # fanout newsfeed to followers. newsfeeds.api.services.py
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializerForList(tweet).data, status=201)

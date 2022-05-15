from newsfeeds.services import NewsFeedService
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from tweets.services import TweetService
from utils.decorators import required_params
from utils.paginations import EndlessPagination


class TweetViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows users to create, list tweets
    """
    # self.get_queryset() will execute the queryset ORM;
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination

    def get_permissions(self):
        """
        Assign permission requirement for each method
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        # <HOMEWORK 1> 通过某个 query 参数 with_all_comments 来决定是否需要带上所有 comments
        # <HOMEWORK 2> 通过某个 query 参数 with_preview_comments 来决定是否需要带上前三条 comments
        # tweet = self.get_object()

        # if request.query_params['with_all_comments'] == "1":
        #     return Response(TweetSerializerWithComments(tweet).data)
        # if request.query_params['with_preview_comments'] == "1":
        #     return Response(TweetSerializerWithComments(tweet).data[:3])
        serializer = TweetSerializerForDetail(
            self.get_object(),
            context={'request': request},
        )
        return Response(serializer.data)

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        """
        重载 list 方法，不列出所有 tweets，必须要求指定 user_id 作为筛选条件
        """
        # 这句查询会被翻译为
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # 这句 SQL 查询会用到 user 和 created_at 的联合索引
        # 单纯的 user 索引是不够的

        # improvement 1: prefetch_related, get rid of N + 1 queries problem
        # improvement 2: cache
        # tweets = TweetService.get_cached_tweets(user_id=request.query_params['user_id'])
        # tweets = self.paginate_queryset(tweets)
        user_id = request.query_params['user_id']
        cached_tweets = TweetService.get_cached_tweets(user_id)
        page = self.paginator.paginate_cached_list(cached_tweets, request)
        if page is None:
         # 这句查询会被翻译为
         # select * from twitter_tweets
         # where user_id = xxx
         # order by created_at desc
         # 这句 SQL 查询会用到 user 和 created_at 的联合索引
         # 单纯的 user 索引是不够的
         queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
         page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            instance=page,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

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
        serializer = TweetSerializer(tweet, context={'request': request})
        return Response(serializer.data, status=201)

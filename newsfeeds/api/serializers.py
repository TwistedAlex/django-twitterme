from rest_framework import serializers
from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializerForList


class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializerForList()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'tweet')

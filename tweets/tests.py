from testing.testcases import TestCase
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def setUp(self):
        self.alex = self.create_user('alex')
        self.tweet = self.create_tweet(self.alex, content='Jiuzhang Dafa Hao')

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.alex, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.alex, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        bob = self.create_user('bob')
        self.create_like(bob, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)
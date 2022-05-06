from rest_framework.test import APIClient
from testing.testcases import TestCase


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.alex = self.create_user('alex')
        self.alex_client = APIClient()
        self.alex_client.force_authenticate(self.alex)

        self.bob = self.create_user('bob')
        self.bob_client = APIClient()
        self.bob_client.force_authenticate(self.bob)

    def test_list(self):
        # anonymous client需要登录
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # 不能用 post
        response = self.alex_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # 一开始啥都没有
        response = self.alex_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # 自己发的信息是可以看到的
        self.alex_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.alex_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        # 关注之后可以看到别人发的
        self.alex_client.post(FOLLOW_URL.format(self.bob.id))
        response = self.bob_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.alex_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)

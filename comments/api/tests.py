from testing.testcases import TestCase
from rest_framework.test import APIClient


COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.alex = self.create_user('alex')
        self.alex_client = APIClient()
        self.alex_client.force_authenticate(self.alex)
        self.bob = self.create_user('bob')
        self.bob_client = APIClient()
        self.bob_client.force_authenticate(self.bob)

        self.tweet = self.create_tweet(self.alex)

    def test_create(self):
        # 匿名不可以创建
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # 啥参数都没带不行
        response = self.alex_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # 只带 tweet_id 不行
        response = self.alex_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)
        # check the last 4 lines: assertEqual(response.data['...'], )

        # 只带 content 不行
        response = self.alex_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # content 太长不行
        response = self.alex_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # tweet_id 和 content 都带才行
        response = self.alex_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.alex.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

from friendships.services import FriendshipService
from gatekeeper.models import GateKeeper
from rest_framework import status
from rest_framework.test import APIClient
from testing.testcases import TestCase
from utils.paginations import EndlessPagination

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        super(FriendshipApiTests, self).setUp()
        self.alex = self.create_user(username='alex')
        self.alex_client = APIClient()
        self.alex_client.force_authenticate(self.alex)

        self.bob = self.create_user(username='bob')
        self.bob_client = APIClient()
        self.bob_client.force_authenticate(self.bob)

        # create followings and followers for bob
        for i in range(2):
            follower = self.create_user('bob_follower{}'.format(i))
            self.create_friendship(from_user=follower, to_user=self.bob)
        for i in range(3):
            following = self.create_user('bob_following{}'.format(i))
            self.create_friendship(from_user=self.bob, to_user=following)

    # def test_follow(self):
    #     # test in mysql
    #     self._test_follow()
    #     self.clear_cache()
    #     GateKeeper.set_kv('switch_friendship_to_hbase', 'percent', 100)
    #     # test in hbase
    #     self._test_follow()

    def test_follow(self):
        url = FOLLOW_URL.format(self.alex.id)

        # 验证需要登录才能 follow 别人
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # 验证要用 get 来 follow
        response = self.bob_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # 验证不可以 follow 自己
        response = self.alex_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # follow 成功
        response = self.bob_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 重复 follow 静默成功
        response = self.bob_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['duplicate'], True)
        # 验证反向关注会创建新的数据
        before_count = FriendshipService.get_following_count(self.alex.id)
        response = self.alex_client.post(FOLLOW_URL.format(self.bob.id))
        after_count = FriendshipService.get_following_count(self.alex.id)
        self.assertEqual(after_count, before_count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.alex.id)

        # 验证需要登录才能 unfollow 别人
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # 验证不能用 get 来 unfollow 别人
        response = self.bob_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # 验证不能用 unfollow 自己
        response = self.alex_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # unfollow 成功
        self.create_friendship(from_user=self.bob, to_user=self.alex)
        before_count = FriendshipService.get_following_count(self.bob.id)
        response = self.bob_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 1)
        after_count = FriendshipService.get_following_count(self.bob.id)
        self.assertEqual(after_count, before_count - 1)

        # 验证未 follow 的情况下 unfollow 静默处理
        before_count = FriendshipService.get_following_count(self.bob.id)
        response = self.bob_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 0)  # 未删掉任何数据
        after_count = FriendshipService.get_following_count(self.bob.id)
        self.assertEqual(before_count, after_count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.bob.id)
        # 验证不能用 post
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # 用 get 成功获取
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        # 验证按照时间倒序
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        ts2 = response.data['results'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'bob_following2',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'bob_following1',
        )
        self.assertEqual(
            response.data['results'][2]['user']['username'],
            'bob_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.bob.id)
        # 验证不能用 post
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # 用 get 成功获取
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        # 验证按照时间倒序
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'bob_follower1',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'bob_follower0',
        )

    def test_followers_pagination(self):
        page_size = EndlessPagination.page_size
        friendships = []
        for i in range(page_size * 2):
            follower = self.create_user('alex_follower{}'.format(i))
            friendship = self.create_friendship(from_user=follower, to_user=self.alex)
            friendships.append(friendship)
            if follower.id % 2 == 0:
                self.create_friendship(from_user=self.bob, to_user=follower)

        url = FOLLOWERS_URL.format(self.alex.id)
        self._paginate_until_the_end(url, 2, friendships)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # bob has followed users with even id
        response = self.bob_client.get(url)
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

    def test_followings_pagination(self):
        page_size = EndlessPagination.page_size
        friendships = []
        for i in range(page_size * 2):
            following = self.create_user('alex_following{}'.format(i))
            friendship = self.create_friendship(from_user=self.alex, to_user=following)
            friendships.append(friendship)
            if following.id % 2 == 0:
                self.create_friendship(from_user=self.bob, to_user=following)

        url = FOLLOWINGS_URL.format(self.alex.id)
        self._paginate_until_the_end(url, 2, friendships)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # bob has followed users with even id
        response = self.bob_client.get(url)
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

        # alex has followed all her following users
        response = self.alex_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)

        # test pull new friendships
        last_created_at = friendships[-1].created_at
        response = self.alex_client.get(url, {'created_at__gt': last_created_at})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        new_friends = [self.create_user('big_v{}'.format(i)) for i in range(3)]
        new_friendships = []
        for friend in new_friends:
            new_friendships.append(self.create_friendship(from_user=self.alex, to_user=friend))
        response = self.alex_client.get(url, {'created_at__gt': last_created_at})
        self.assertEqual(len(response.data['results']), 3)
        for result, friendship in zip(response.data['results'], reversed(new_friendships)):
            self.assertEqual(result['created_at'], friendship.created_at)

    def _paginate_until_the_end(self, url, expect_pages, friendships):
        results, pages = [], 0
        # 默认的第一页
        response = self.anonymous_client.get(url)
        results.extend(response.data['results'])

        pages += 1
        while response.data['has_next_page']:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # 根据前一页的最后一个 item 的 created_at 作为下一页的范围
            last_item = response.data['results'][-1]
            response = self.anonymous_client.get(url, {
                'created_at__lt': last_item['created_at'],
            })
            results.extend(response.data['results'])
            pages += 1

        self.assertEqual(len(results), len(friendships))
        self.assertEqual(pages, expect_pages)
        # friendship is in ascending order, results is in descending order
        for result, friendship in zip(results, friendships[::-1]):
            self.assertEqual(result['created_at'], friendship.created_at)
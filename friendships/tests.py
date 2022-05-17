from django_hbase.models import BadRowKeyError, EmptyColumnError
from friendships.hbase_models import HBaseFollowing, HBaseFollower
from friendships.models import Friendship
from friendships.services import FriendshipService
from testing.testcases import TestCase
import time


class FriendshipServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.alex = self.create_user('alex')
        self.bob = self.create_user('bob')

    def test_get_followings(self):
        user1 = self.create_user('user1')
        user2 = self.create_user('user2')
        for to_user in [user1, user2, self.bob]:
            Friendship.objects.create(from_user=self.alex, to_user=to_user)

        user_id_set = FriendshipService.get_following_user_id_set(self.alex.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id, self.bob.id})

        Friendship.objects.filter(from_user=self.alex, to_user=self.bob).delete()
        user_id_set = FriendshipService.get_following_user_id_set(self.alex.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id})

    class HBaseTests(TestCase):

        @property
        def ts_now(self):
            return int(time.time() * 1000000)

        def test_save_and_get(self):
            # validate save and get
            timestamp = self.ts_now
            following = HBaseFollowing(from_user_id=123, to_user_id=34, created_at=timestamp)
            following.save()

            instance = HBaseFollowing.get(from_user_id=123, created_at=timestamp)
            self.assertEqual(instance.from_user_id, 123)
            self.assertEqual(instance.to_user_id, 34)
            self.assertEqual(instance.created_at, timestamp)

            # update the object
            following.to_user_id = 456
            following.save()

            instance = HBaseFollowing.get(from_user_id=123, created_at=timestamp)
            self.assertEqual(instance.to_user_id, 456)

            # object does not exist, return None
            instance = HBaseFollowing.get(from_user_id=123, created_at=self.ts_now)
            self.assertEqual(instance, None)

        def test_create_and_get(self):
            # missing column data, can not store in hbase
            # check if exception is raised properly
            try:
                HBaseFollower.create(to_user_id=1, created_at=self.ts_now)
                exception_raised = False
            except EmptyColumnError:
                exception_raised = True
            self.assertEqual(exception_raised, True)

            # invalid row_key
            try:
                HBaseFollower.create(from_user_id=1, to_user_id=2)
                exception_raised = False
            except BadRowKeyError as e:
                exception_raised = True
                self.assertEqual(str(e), 'created_at is missing in row key')
            self.assertEqual(exception_raised, True)

            ts = self.ts_now
            HBaseFollower.create(from_user_id=1, to_user_id=2, created_at=ts)
            instance = HBaseFollower.get(to_user_id=2, created_at=ts)
            self.assertEqual(instance.from_user_id, 1)
            self.assertEqual(instance.to_user_id, 2)
            self.assertEqual(instance.created_at, ts)

            # can not get if row key missing
            # check if exception is raised properly
            try:
                HBaseFollower.get(to_user_id=2)
                exception_raised = False
            except BadRowKeyError as e:
                exception_raised = True
                self.assertEqual(str(e), 'created_at is missing in row key')
            self.assertEqual(exception_raised, True)

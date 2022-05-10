from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def setUp(self):
        self.alex = self.create_user('alex')
        self.tweet = self.create_tweet(self.alex)
        self.comment = self.create_comment(self.alex, self.tweet)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like_set(self):
        self.create_like(self.alex, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.alex, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        bob = self.create_user('bob')
        self.create_like(bob, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)

from utils.listeners import invalidate_object_cache


def incr_comments_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    # handle new comment
    Tweet.objects.filter(id=instance.tweet_id)\
     .update(comments_count=F('comments_count') + 1)
    # update 操作不会触发 invalidate_object_cache
    # 想让它触发 tweet 的 post_save 逻辑，就要手动触发
    invalidate_object_cache(sender=Tweet, instance=instance.tweet)


def decr_comments_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    # handle comment deletion
    Tweet.objects.filter(id=instance.tweet_id)\
        .update(comments_count=F('comments_count') - 1)
    invalidate_object_cache(sender=Tweet, instance=instance.tweet)

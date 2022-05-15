def incr_likes_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    # 查看是否是 tweet 的 like
    # 因为 like 可以同时记录 tweet 的 like 和 comment 的 like
    # 但此处我们只 denormalize 了 tweet 的 like
    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # TODO: 给 Comment 使用类似的方法进行 likes_count 的统计
        return

    # handle new tweet like

    # 不可以使用 tweet.likes_count += 1; tweet.save() 的方式
    # 因此这个操作不是原子操作，必须使用 update 语句才是原子操作
    # SQL Query:
    # UPDATE likes_count = likes_count + 1
    # FROM tweets_table
    # WHERE id=<instance.object_id>

    # 方法 1
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') + 1)
    # 想要 likes_count 的更新不要与 tweet 的更新绑在一起，否则 cache 会一直 miss
    # 不想让它触发 tweet 的 post_save 逻辑，就不需要 invalidate_object_cache

    # 方法 2
    # tweet = instance.content_object
    # tweet.likes_count = F('likes_count') + 1
    # tweet.save()


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # TODO: HOMEWORK 给 Comment 使用类似的方法进行 likes_count 的统计
        return

    # handle tweet likes cancel
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') - 1)

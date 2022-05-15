def push_newsfeed_to_cache(sender, instance, created, **kwargs):
    # created 原本是藏在 kwargs 中，但我们需要这个参数，就单独写
    if not created:
        return

    from newsfeeds.services import NewsFeedService
    NewsFeedService.push_newsfeed_to_cache(instance)
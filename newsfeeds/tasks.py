from celery import shared_task
from friendships.services import FriendshipService
from newsfeeds.constants import FANOUT_BATCH_SIZE
from newsfeeds.models import NewsFeed
from utils.time_constants import ONE_HOUR


@shared_task(routing_key='newsfeeds', time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, follower_ids):
    # import 写在里面避免循环依赖
    from newsfeeds.services import NewsFeedService

    # 错误的方法
    # 不可以将数据库操作放在 for 循环里面，效率会非常低
    # for follower in FriendshipService.get_followers(tweet.user):
    #     NewsFeed.objects.create(
    #         user=follower,
    #         tweet=tweet,
    #     )
    # 正确的方法：使用 bulk_create，会把 insert 语句合成一条

    # 获取当前发帖人的所有粉丝
    newsfeeds = [
        NewsFeed(user_id=follower_id, tweet_id=tweet_id)
        for follower_id in follower_ids
    ]

    # 一次性写入
    NewsFeed.objects.bulk_create(objs=newsfeeds)

    # bulk create 不会触发 post_save 的 signal，所以需要手动 push 到 cache 里
    # post_save 的 signal 只会单个触发，不会批量触发，所以得手动写触发机制
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)

    return '{} newsfeeds created'.format(len(newsfeeds))
    # 其实若是一个 1kw 粉丝的博主发了一个 144字节的 tweet，
    # 如果把整个 tweet 去 fan out 到 1kw 粉丝中，会给 redis 的内存带来 1G 的耗费
    # 可进一步优化：在 newsfeed cache 中，不直接存储整个 tweet，而是只存 tweet id
    # 即不是把整个 newsfeed push 进 cache，而是只是 push 有哪些 id
    # 但这里可以不优化的原因：newsfeed 在 serialize 时，
    # 只有 user_id，tweet_id，和 created_at，并没有整条 tweet


@shared_task(routing_key='default', time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, tweet_user_id):
    # 将推给自己的 Newsfeed 率先创建，确保自己能最快看到
    NewsFeed.objects.create(user_id=tweet_user_id, tweet_id=tweet_id)

    # 在具体的 async task 中进行拆分，拆成一个个小的 async task

    # 获得所有的 follower ids，按照 batch size 拆分开
    follower_ids = FriendshipService.get_follower_ids(tweet_user_id)
    index = 0
    while index < len(follower_ids):
        batch_ids = follower_ids[index: index + FANOUT_BATCH_SIZE]
        fanout_newsfeeds_batch_task.delay(tweet_id, batch_ids) # 拆成小的async task
        index += FANOUT_BATCH_SIZE

    return '{} newsfeeds going to fanout, {} batches created.'.format(
        len(follower_ids),
        (len(follower_ids) - 1) // FANOUT_BATCH_SIZE + 1,
    )

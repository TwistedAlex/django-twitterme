from django_hbase import models


class HBaseFollowing(models.HBaseModel):
    """
    存储 from_user_id follow 了哪些人，row_key 按照 from_user_id + created_at 排序
    可以支持查询：
    - A 关注的所有人按照关注时间排序
    - A 在某个时间段内关注的人有哪些
    - A 在某个时间点之后/之前关注的前 X 个人是谁
    """
    # row key
    from_user_id = models.IntegerField(reverse=True)  # 翻转
    created_at = models.TimestampField()
    # column key
    to_user_id = models.IntegerField(column_family='cf')

    class Meta:
        table_name = 'twitter_followings'
        row_key = ('from_user_id', 'created_at')


class HBaseFollower(models.HBaseModel):
    """
    存储 to_user_id 被哪些人 follow 了，row_key 按照 to_user_id + created_at 排序
    可以支持查询：
    - A 的所有粉丝按照关注时间排序
    - A 在某个时间段内被哪些粉丝关注了
    - 哪 X 人在某个时间点之后/之前关注了 A
    """
    # row key
    to_user_id = models.IntegerField(reverse=True)  # 翻转
    created_at = models.TimestampField()
    # column key
    from_user_id = models.IntegerField(column_family='cf')

    class Meta:
        row_key = ('to_user_id', 'created_at')
        table_name = 'twitter_followers'

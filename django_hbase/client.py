import happybase
from django.conf import settings


class HBaseClient:
    conn = None

    @classmethod
    def get_connection(cls):
        # 使用 singleton 模式，全局只创建一个 connection
        if cls.conn:
            return cls.conn

        cls.conn = happybase.Connection(settings.HBASE_HOST)
        return cls.conn

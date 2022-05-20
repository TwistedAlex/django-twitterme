from utils.redis_client import RedisClient


class GateKeeper:

    @classmethod
    def get(cls, gk_name):
        conn = RedisClient.get_connection()
        name = f'gatekeeper:{gk_name}'
        if not conn.exists(name):
            return {
                'percent': 0,
                'description': '',
            }

        redis_hash = conn.hgetall(name)  # 得到所有 (key, value)
        return {
            'percent': int(redis_hash.get(b'percent', 0)),
            'description': str(redis_hash.get(b'description', '')),
        }

    @classmethod
    def set_kv(cls, gk_name, key, value):
        conn = RedisClient.get_connection()
        name = f'gatekeeper:{gk_name}'
        conn.hset(name, key, value)  # 为哈希表中的字段赋值

    @classmethod
    def is_switch_on(cls, gk_name):
        return cls.get(gk_name)['percent'] == 100

    @classmethod
    def turn_on(cls, gk_name):
        cls.set_kv(gk_name, 'percent', 100)

    @classmethod
    def in_gk(cls, gk_name, user_id):
        # 开放的用户数的百分比
        return user_id % 100 < cls.get(gk_name)['percent']
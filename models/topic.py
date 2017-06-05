import time
from models import Model
from models.user import User
from models.mongua import Mongua
import json
import logging
ogger = logging.getLogger("bbs")


class Topic(Model):
    @classmethod
    def get(cls, id):
        m = cls.find_by(id=id)
        m.views += 1
        m.save()
        return m

    def __init__(self, form):
        self.id = None
        self.views = 0
        self.title = form.get('title', '')
        self.content = form.get('content', '')
        self.ct = int(time.time())
        self.ut = self.ct
        self.user_id = form.get('user_id', '')
        self.board_id = int(form.get('board_id', -1))
        self.istop = False
        self.last_time = None

    def replies(self):
        from .reply import Reply
        ms = Reply.find_all(topic_id=self.id)
        return ms

    def board(self):
        from .board import Board
        m = Board.find(self.board_id)
        return m

    def user(self):
        u = User.find(id=self.user_id)
        return u

    def set_time(self):
        self.last_time = int(time.time())
        self.save()

    @staticmethod
    def top():
        m = Topic.find_all(istop=True)
        return m

    @staticmethod
    def notop():
        m = Topic.find_all(istop=False)
        return m


class Cache(object):
    def get(self, key):
        pass

    def set(self, key, value):
        pass


class MemoryCache(Cache):
    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache[key]

    def set(self, key, value):
        self.cache[key] = value


class RedisCache(Cache):
    import redis
    redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

    def set(self, key, value):
        return RedisCache.redis_db.set(key, value)

    def get(self, key):
        return RedisCache.redis_db.get(key)


class Topic(Mongua):
    __fields__ = Mongua.__fields__ + [
        ('content', str, ''),
        ('user_id', int, -1),
        ('board_id', int, -1),
        ('views', int, 0),
        ('istop', bool, False),
        ('last_time', int, None),
        ('title', str, ''),
        ('last_reply_id', str, None)
    ]
    should_update_all = True
    # 1. memory cache
    cache = MemoryCache()
    # 2. redis cahce
    redis_cache = RedisCache()

    def to_json(self):
        d = dict()
        for k in Topic.__fields__:
            key = k[0]
            if not key.startswith('_'):
                d[key] = getattr(self, key)
        return json.dumps(d)

    @classmethod
    def from_json(cls, j):
        d = json.loads(j)

        instance = cls()
        for k, v in d.items():
            setattr(instance, k, v)
        return instance

    @classmethod
    def all_delay(cls):
        # time.sleep(3)
        # return Topic.all()
        return Topic.notop()

    @classmethod
    def get(cls, id):
        m = cls.find_by(id=id)
        m.views += 1
        m.save()
        return m

    def save(self):
        super(Topic, self).save()
        Topic.should_update_all = True

    @classmethod
    def cache_all(cls):

        # 2. redis cache
        if Topic.should_update_all:
            Topic.redis_cache.set('topic_all', json.dumps([i.to_json() for i in cls.all_delay()]))
            Topic.should_update_all = False
        j = json.loads(Topic.redis_cache.get('topic_all').decode('utf-8'))
        j = [Topic.from_json(i) for i in j]
        return j

    def replies(self):
        from .reply import Reply
        ms = Reply.find_all(topic_id=self.id)
        return ms

    def board(self):
        from .board import Board
        m = Board.find(self.board_id)
        return m

    def user(self):
        u = User.find(id=self.user_id)
        return u

    @staticmethod
    def top():
        m = Topic.find_all(istop=True)
        return m

    @staticmethod
    def notop():
        m = Topic.find_all(istop=False)
        return m

    def set_time(self):
        self.last_time = int(time.time())
        self.save()

    def last_replier(self):
        from .user import User
        u = User.find(self.last_reply_id)
        return u

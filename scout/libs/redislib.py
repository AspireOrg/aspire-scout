from redis import Redis

class RedisLib(object):
    app = None
    redis_cli = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        if app.config.get("TESTING", False):
            from mockredis import MockRedis
            self.redis_cli = MockRedis()
        else:
            self.redis_cli = Redis(host=app.config['REDIS_HOST'], port=app.config.get('REDIS_PORT', 6379), db=app.config.get('REDIS_DB', 0))

    def __getattr__(self, name):
        return getattr(self.redis_cli, name)

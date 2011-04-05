
class NewsRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'news_app':
            return 'news_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'news_app':
            return 'news_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'news_app' or obj2._meta.app_label == 'news_app':
            return True
        return None

    def allow_syncdb(self, db, model):
        if db == 'news_db':
            return model._meta.app_label == 'news_app'
        elif model._meta.app_label == 'news_app':
            return False
        return None


class FruitRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'fruit_app':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'fruit_app':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'fruit_app' or obj2._meta.app_label == 'fruit_app':
            return True
        return None

    def allow_syncdb(self, db, model):
        if db == 'default':
            if model._meta.app_label == 'fruit_app':
                return True
        elif model._meta.app_label == 'fruit_app':
            return False
        return None

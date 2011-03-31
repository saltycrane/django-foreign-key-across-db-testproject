from django.db import models


class FruitManager(models.Manager):

    def __init__(self, *args, **kwargs):
        self.forced_using = kwargs.pop('using', 'default')
        super(FruitManager, self).__init__(*args, **kwargs)


class Fruit(models.Model):
    name = models.CharField(max_length=20)

    objects = FruitManager(using='default')

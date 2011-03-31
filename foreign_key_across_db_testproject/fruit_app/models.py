from django.db import models


class FruitManager(models.Manager):
    forced_using = 'default'


class Fruit(models.Model):
    name = models.CharField(max_length=20)

    objects = FruitManager()

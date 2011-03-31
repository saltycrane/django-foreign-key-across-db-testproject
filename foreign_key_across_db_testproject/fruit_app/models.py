from django.db import models


class Fruit(models.Model):
    name = models.CharField(max_length=20)

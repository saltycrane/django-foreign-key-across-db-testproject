from django.db import models

from foreign_key_across_db_testproject.fields import ForeignKeyAcrossDb
from foreign_key_across_db_testproject.fruit_app.models import Fruit


class Article(models.Model):
    fruit = ForeignKeyAcrossDb(Fruit)
    intro = models.TextField()

    def fruit_name(self):
        print self.fruit
        return self.fruit.name

from django.db import models

from foreign_key_across_db_testproject.fruit_app.models import Fruit


class Article(models.Model):
    fruit = models.ForeignKey(Fruit)
    intro = models.TextField()

    def fruit_name(self):
        return self.fruit.name

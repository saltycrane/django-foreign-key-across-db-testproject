from django.db import models

class Article(models.Model):
    fruit = models.ForeignKey('fruit_app.Fruit')
    intro = models.TextField()

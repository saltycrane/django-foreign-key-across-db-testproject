from django.db import models

from foreign_key_across_db_testproject.fields import ForeignKeyAcrossDb
from foreign_key_across_db_testproject.fruit_app.models import Fruit


class Article(models.Model):
    fruit = ForeignKeyAcrossDb(Fruit)
    intro = models.TextField()

    # TODO: shouldn't need fruit_obj if ForeignKeyAcrossDb field worked properly
    @property
    def fruit_obj(self):
        if not hasattr(self, '_fruit_obj'):
            # TODO: why is it sometimes an int and sometimes a Fruit object?
            if isinstance(self.fruit, int) or isinstance(self.fruit, long):
                print 'self.fruit IS a number'
                self._fruit_obj = Fruit.objects.get(pk=self.fruit)
            else:
                print 'self.fruit IS NOT a number'
                self._fruit_obj = self.fruit
        return self._fruit_obj

    def fruit_name(self):
        return self.fruit_obj.name

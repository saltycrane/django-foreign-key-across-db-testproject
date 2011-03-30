from django.db import models


class ForeignKeyAcrossDb(models.IntegerField):
    '''
    Exists because foreign keys do not work across databases
    '''
    def __init__(self, model_on_other_db, **kwargs):
        self.model_on_other_db = model_on_other_db
        super(ForeignKeyAcrossDb, self).__init__(**kwargs)

    def to_python(self, value):
        # TODO: this db lookup is duplicated in get_prep_lookup()
        if isinstance(value, self.model_on_other_db):
            return value
        else:
            return self.model_on_other_db._default_manager.get(pk=value)

    def get_prep_value(self, value):
        if isinstance(value, self.model_on_other_db):
            value = value.pk
        return super(ForeignKeyAcrossDb, self).get_prep_value(value)

    def get_prep_lookup(self, lookup_type, value):
        # TODO: this db lookup is duplicated in to_python()
        if not isinstance(value, self.model_on_other_db):
            value = self.model_on_other_db._default_manager.get(pk=value)

        return super(ForeignKeyAcrossDb, self).get_prep_lookup(lookup_type, value)

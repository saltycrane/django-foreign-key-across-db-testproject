from django.db import models
from django.db import router
from django.db.models.query import QuerySet


class ReverseSingleRelatedObjectDescriptor(object):
    # This class provides the functionality that makes the related-object
    # managers available as attributes on a model class, for fields that have
    # a single "remote" value, on the class that defines the related field.
    # In the example "choice.poll", the poll attribute is a
    # ReverseSingleRelatedObjectDescriptor instance.
    def __init__(self, field_with_rel):
        self.field = field_with_rel

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        cache_name = self.field.get_cache_name()
        try:
            return getattr(instance, cache_name)
        except AttributeError:
            val = getattr(instance, self.field.attname)
            if val is None:
                # If NULL is an allowed value, return it.
                if self.field.null:
                    return None
                raise self.field.rel.to.DoesNotExist
            other_field = self.field.rel.get_related_field()
            if other_field.rel:
                params = {'%s__pk' % self.field.rel.field_name: val}
            else:
                params = {'%s__exact' % self.field.rel.field_name: val}

            # If the related manager indicates that it should be used for
            # related fields, respect that.
            rel_mgr = self.field.rel.to._default_manager
            db = router.db_for_read(self.field.rel.to, instance=instance)
            if getattr(rel_mgr, 'forced_using', False):
                db = rel_mgr.forced_using
                rel_obj = rel_mgr.using(db).get(**params)
            elif getattr(rel_mgr, 'use_for_related_fields', False):
                rel_obj = rel_mgr.using(db).get(**params)
            else:
                rel_obj = QuerySet(self.field.rel.to).using(db).get(**params)
            setattr(instance, cache_name, rel_obj)
            return rel_obj

    def __set__(self, instance, value):
        raise NotImplementedError()


class ForeignKeyAcrossDb(models.ForeignKey):

    def contribute_to_class(self, cls, name):
        models.ForeignKey.contribute_to_class(self, cls, name)
        setattr(cls, self.name, ReverseSingleRelatedObjectDescriptor(self))
        if isinstance(self.rel.to, basestring):
            target = self.rel.to
        else:
            target = self.rel.to._meta.db_table
        cls._meta.duplicate_targets[self.column] = (target, "o2m")

    def validate(self, value, model_instance):
        pass

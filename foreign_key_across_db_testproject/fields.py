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
            if getattr(rel_mgr, 'use_for_related_fields', False):
                rel_obj = rel_mgr.using(db).get(**params)
            else:
                rel_obj = QuerySet(self.field.rel.to).using(db).get(**params)
            setattr(instance, cache_name, rel_obj)
            return rel_obj

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("%s must be accessed via instance" % self._field.name)

        # If null=True, we can assign null here, but otherwise the value needs
        # to be an instance of the related class.
        if value is None and self.field.null == False:
            raise ValueError('Cannot assign None: "%s.%s" does not allow null values.' %
                                (instance._meta.object_name, self.field.name))
        elif value is not None and not isinstance(value, self.field.rel.to):
            raise ValueError('Cannot assign "%r": "%s.%s" must be a "%s" instance.' %
                                (value, instance._meta.object_name,
                                 self.field.name, self.field.rel.to._meta.object_name))
        elif value is not None:
            if instance._state.db is None:
                instance._state.db = router.db_for_write(instance.__class__, instance=value)
            elif value._state.db is None:
                value._state.db = router.db_for_write(value.__class__, instance=instance)
            elif value._state.db is not None and instance._state.db is not None:
                if not router.allow_relation(value, instance):
                    raise ValueError('Cannot assign "%r": instance is on database "%s", value is on database "%s"' %
                                        (value, instance._state.db, value._state.db))

        # If we're setting the value of a OneToOneField to None, we need to clear
        # out the cache on any old related object. Otherwise, deleting the
        # previously-related object will also cause this object to be deleted,
        # which is wrong.
        if value is None:
            # Look up the previously-related object, which may still be available
            # since we've not yet cleared out the related field.
            # Use the cache directly, instead of the accessor; if we haven't
            # populated the cache, then we don't care - we're only accessing
            # the object to invalidate the accessor cache, so there's no
            # need to populate the cache just to expire it again.
            related = getattr(instance, self.field.get_cache_name(), None)

            # If we've got an old related object, we need to clear out its
            # cache. This cache also might not exist if the related object
            # hasn't been accessed yet.
            if related:
                cache_name = self.field.related.get_cache_name()
                try:
                    delattr(related, cache_name)
                except AttributeError:
                    pass

        # Set the value of the related field
        try:
            val = getattr(value, self.field.rel.get_related_field().attname)
        except AttributeError:
            val = None
        setattr(instance, self.field.attname, val)

        # Since we already know what the related object is, seed the related
        # object cache now, too. This avoids another db hit if you get the
        # object you just set.
        setattr(instance, self.field.get_cache_name(), value)


class ForeignKeyAcrossDb(models.ForeignKey):

    def validate(self, value, model_instance):
        if self.rel.parent_link:
            return
        super(ForeignKey, self).validate(value, model_instance)
        if value is None:
            return

        qs = self.rel.to._default_manager.filter(**{self.rel.field_name:value})
        qs = qs.complex_filter(self.rel.limit_choices_to)
        if not qs.exists():
            raise exceptions.ValidationError(self.error_messages['invalid'] % {
                'model': self.rel.to._meta.verbose_name, 'pk': value})

    def contribute_to_class(self, cls, name):
        super(ForeignKey, self).contribute_to_class(cls, name)
        setattr(cls, self.name, ReverseSingleRelatedObjectDescriptor(self))
        if isinstance(self.rel.to, basestring):
            target = self.rel.to
        else:
            target = self.rel.to._meta.db_table
        cls._meta.duplicate_targets[self.column] = (target, "o2m")

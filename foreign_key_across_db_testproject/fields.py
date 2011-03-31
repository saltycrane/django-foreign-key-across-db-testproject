from django.core import exceptions
from django.db import models
from django.db import router


class ForeignKeyAcrossDb(models.ForeignKey):

    def validate(self, value, model_instance):
        if self.rel.parent_link:
            return
        models.Field.validate(self, value, model_instance)
        if value is None:
            return

        using = router.db_for_read(self.rel.to, instance=model_instance)  # is this more correct than Django's 1.2.5 version?
        qs = self.rel.to._default_manager.using(using).filter(
                **{self.rel.field_name: value}
             )
        qs = qs.complex_filter(self.rel.limit_choices_to)
        if not qs.exists():
            raise exceptions.ValidationError(self.error_messages['invalid'] % {
                'model': self.rel.to._meta.verbose_name, 'pk': value})

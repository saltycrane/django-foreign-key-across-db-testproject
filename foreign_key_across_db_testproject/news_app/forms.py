from django.forms import ModelChoiceField
from django.forms.models import ModelForm

from foreign_key_across_db_testproject.fruit_app.models import Fruit
from foreign_key_across_db_testproject.news_app.models import Article


class FruitChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class ArticleAdminForm(ModelForm):
    fruit = FruitChoiceField(Fruit.objects.all().order_by('name'))

    class Meta:
        model = Article

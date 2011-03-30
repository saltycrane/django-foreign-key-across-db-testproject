from django.contrib import admin

from foreign_key_across_db_testproject.news_app.forms import ArticleAdminForm
from foreign_key_across_db_testproject.news_app.models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('fruit_name',)
    form = ArticleAdminForm


admin.site.register(Article, ArticleAdmin)

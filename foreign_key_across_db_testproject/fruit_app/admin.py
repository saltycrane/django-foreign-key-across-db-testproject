from django.contrib import admin

from foreign_key_across_db_testproject.fruit_app.models import Fruit


class FruitAdmin(admin.ModelAdmin):
    pass


admin.site.register(Fruit, FruitAdmin)

from django.contrib import admin
from .models import Feed, Article, News_Category

# Register your models here.

admin.site.register(Feed)
admin.site.register(Article)
admin.site.register(News_Category)
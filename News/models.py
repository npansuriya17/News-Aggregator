from django.db import models
from django import forms

# Create your models here.

class News_Category(models.Model):
    category = models.CharField(max_length=30)
    
    def __str__(self):
        return self.category


class Feed(models.Model):
    feed_category = models.ForeignKey(News_Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    url = models.URLField()
    isActive = models.BooleanField(default=False)

    def __str__(self):
        return '%s %s' % (self.title, self.feed_category)


class Article(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=1000)
    url = models.URLField()
    summary = models.TextField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    publication_date = models.DateTimeField()

    def __str__(self):
        return '%s %s %s %s %s' % (self.feed, self.title, self.url, self.description, self.publication_date)
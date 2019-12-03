"""
Comments may be attached to any object. See the comment documentation for
more information.
"""

from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Article(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    headline = models.CharField(max_length=100)

    def __str__(self):
        return self.headline


class Entry(models.Model):
    title = models.CharField(max_length=250)
    body = models.TextField()
    pub_date = models.DateField()
    enable_comments = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Book(models.Model):
    dewey_decimal = models.DecimalField(primary_key=True, decimal_places=2, max_digits=5)

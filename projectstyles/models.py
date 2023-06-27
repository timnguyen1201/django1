from django.utils import timezone
import datetime
from django.db import models
from django.db.models import DEFERRED
from django.contrib import admin


# Define the models - database layout, with additional metadata
# Question has a question and a publication date

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


# Choices has 2 fields: the text of choice and a vote tally
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Book(models.Model):
    title = models.CharField(max_length=20)

    def create(self, title):
        book = self(title=title)
        return book


class BookManager(models.Manager):
    def create_book(self, title):
        book = self.create(title=title)
        return book


class Book(models.Model):
    title = models.CharField(max_length=100)
    objects = BookManager()


def from_db(cls, db, field_names, values):
    # Default implementation of from_db() (subject to change and could
    # be replaced with super()
    if len(values) != len(cls._meta.concrete_fields):
        values = list(values)
        values.reverse()
        values = [
            values.pop() if f.attname in field_names else DEFERRED
            for f in cls._meta.concrete_fields
        ]
    instance = cls(*values)
    instance._loaded_values = dict(
        zip(field_names, (value for value in values if value is not DEFERRED))
    )
    return instance


def save(self, *args, **kwargs):
    # Check how the current values differ from ._loaded_values. For examples,
    # prevent changing the creator_id of the model. (This example doesn't
    # support cases where 'creator_id' is deferred).
    if not self._state.adding and (
            self.creator_id != self._loaded_values["creator_id"]
    ):
        raise ValueError("Updating the value of creator isn't allowed")
    super().save(*args, **kwargs)


def was_published_recently(self):
    now = timezone.now()
    return now - datetime.timedelta(days=1) <= self.pub_date <= now

from django.db import models
from datetime import date


class Author(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    birth_year = models.DateField(null=True, blank=True)
    death_year = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.surname} {self.age}"

    @property
    def age(self):
        if self.birth_year:
            if self.death_year:
                return self.death_year.year - self.birth_year.year
            else:
                return date.today().year - self.birth_year.year


class IrAuthor(Author):
    in_iran = models.BooleanField(verbose_name="Lives in Iran")

    class Meta:
        verbose_name = "Iranian Author"


# class Country(models.Model):
#     name = models.CharField(max_length=100)


class Language(models.Model):
    lang_options = [
        ('en', 'English'),
        ('fa', 'Farsi'),
        ('fr', 'French')
    ]
    title = models.CharField(choices=lang_options, max_length=2)
    countries = models.CharField(max_length=250, verbose_name="Countries speaking language")

    def __str__(self):
        return self.get_title_display()

    class Meta:
        ordering = ["title"]


class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING)
    pub_date = models.DateField(verbose_name='Publication Date', null=True, blank=True)
    publisher = models.CharField(max_length=250, null=True, blank=True)
    lang = models.ManyToManyField(Language, verbose_name="Language")


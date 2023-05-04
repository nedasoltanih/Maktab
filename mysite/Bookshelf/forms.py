from django import forms
from Bookshelf.models import Book, Author


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ["author"]


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = "__all__"
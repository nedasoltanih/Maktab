from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views.generic import View

from Bookshelf.forms import BookForm, AuthorForm
from Bookshelf.models import Author, Book


class NewBookView(View):
    def get(self, request):
        bookform = BookForm()
        authorform = AuthorForm()
        return render(request, "bookshelf/new_book_author.html", {'bookform':bookform, 'authorform':authorform})

    def post(self, request):
        bookform = BookForm(request.POST)
        authorform = AuthorForm(request.POST)
        if bookform.is_valid() and authorform.is_valid():
            # author = Author(name=authorform.cleaned_data["name"],
            #                 surname=authorform.cleaned_data["surname"]
            #                 )
            # author.save()
            # book = Book(title=bookform.cleaned_data["title"], author=author)
            # book.save()
            authorform.save()
            book = Book(title=bookform.cleaned_data["title"], author=Author.objects.last())
            book.save()
            return HttpResponseRedirect("/reminder/success/")
        else:
            return render(request, "bookshelf/new_book_author.html", {'bookform': bookform, 'authorform': authorform})

from django.shortcuts import render, redirect
from django.contrib import messages
from exam_app.models import Book, Author, Review
from login_app.models import User


def index(request):
    context = {
        'books': Book.objects.all(),
        'recent_reviews': Review.objects.order_by('created_at').reverse()[:3]
    }
    return render(request,'book_index.html',context)

def add(request):
    context = {
        'authors': Author.objects.all()
    }
    return render(request,'add.html',context)

def create_book(request):
    book_errors = Book.objects.basic_validator(request.POST)
    if len(book_errors) > 0:
        for k, v in book_errors.items():
            messages.error(request, v)

    review_errors = Review.objects.basic_validator(request.POST)
    if len(review_errors) > 0:
        for k, v in review_errors.items():
            messages.error(request, v)

    if request.POST['author_dropdown'] == '':
        if request.POST['author'] == '':
            messages.error(request, "Please add an author name or select an existing author")
        else:
            author_errors = Author.objects.basic_validator(request.POST)
            if len(author_errors) > 0:
                for k, v, in author_errors.items():
                    messages.error(request, v)

    if len(messages.get_messages(request)) > 0:
        return redirect('/books/add')
    else:
        if request.POST['author_dropdown'] == '':
            author = Author.objects.create(name = request.POST['author'])
        else:
            author = Author.objects.get(id = request.POST['author_dropdown'])
        book = Book.objects.create(title=request.POST['title'],author = author)
        user = User.objects.get(id = request.session['user_id'])
        Review.objects.create(review = request.POST['review'], rating = request.POST['rating'], book = book, user = user)
        return redirect(f'/books/{book.id}')

def single_book(request,book_id):
    context = {
        'book': Book.objects.get(id = book_id)
    }
    return render(request, 'single_book.html',context)

def delete_review(request, review_id):
    review = Review.objects.get(id = review_id)
    if review.user.id == request.session['user_id']:
        review.delete()
    else:
        messages.error(request, "this isn't yours to delete.")
    return redirect(f'/books/{review.book.id}')

def create_review(request, book_id):
    review_errors = Review.objects.basic_validator(request.POST)
    if review_errors:
        for k, v in review_errors.items():
            messages.error(request, v)
        return redirect(f'/books/{book_id}')
    else:
        book = Book.objects.get(id = book_id)
        user = User.objects.get(id = request.session['user_id'])
        Review.objects.create(review = request.POST['review'], rating = request.POST['rating'], book = book, user = user)
        return redirect(f'/books/{book_id}')
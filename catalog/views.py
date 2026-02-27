from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Book, Author
from .forms import BookForm, AuthorForm

# Create your views here.
def is_staff(user):
    #Verifica si es staff
    return user.is_staff

#Vista publica
def book_list(request):
    #Listado de los libros
    query = request.GET.get('q', '')
    books = Book.objects.select_related('author').all()
    
    if query:
        #Busqueda por titulo o autor
        books = books.filter(
            Q(title__icontains=query) | 
            Q(author__name__icontains=query)
        )
    
    return render(request, 'catalog/book_list.html', {
        'books': books,
        'query': query,
    })


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'catalog/book_detail.html', {'book': book})


#Vista staff(CRUD)

@login_required
@user_passes_test(is_staff)
def book_create(request):
    #Crea libro
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Libro "{book.title}" creado.')
            return redirect('catalog:book_detail', pk=book.pk)
        messages.error(request, 'Corrige los errores.')
    else:
        form = BookForm()
    
    return render(request, 'catalog/book_form.html', {
        'form': form,
        'action': 'Crear',
    })


@login_required
@user_passes_test(is_staff)
def book_update(request, pk):
    #Edita libro
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Libro "{book.title}" actualizado.')
            return redirect('catalog:book_detail', pk=book.pk)
        messages.error(request, 'Corrige los errores.')
    else:
        form = BookForm(instance=book)
    
    return render(request, 'catalog/book_form.html', {
        'form': form,
        'book': book,
        'action': 'Editar',
    })


@login_required
@user_passes_test(is_staff)
def book_delete(request, pk):
    #Elimina libro
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Libro "{title}" eliminado.')
        return redirect('catalog:book_list')
    
    return render(request, 'catalog/book_confirm_delete.html', {'book': book})


@login_required
@user_passes_test(is_staff)
def author_create(request):
    #Crea autor
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'Autor "{author.name}" creado.')
            return redirect('catalog:book_create')
    else:
        form = AuthorForm()
    
    return render(request, 'catalog/author_form.html', {'form': form})
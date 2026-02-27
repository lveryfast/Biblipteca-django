from django.contrib import admin
from .models import Author, Book

# Register your models here.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    #Busca por nombre de autor
    search_fields = ['name']
    list_display = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    #Muestra los campos, busca, filtra y ordena
    list_display = ['title', 'author', 'isbn', 'is_available']
    search_fields = ['title', 'author__name', 'isbn']
    list_filter = ['is_available', 'author']
    ordering = ['title']
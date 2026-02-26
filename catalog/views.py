from django.shortcuts import render

# Create your views here.
def book_list(request):
    # Vista temporal para probar que el servidor corre
    return render(request, 'catalog/books.html')
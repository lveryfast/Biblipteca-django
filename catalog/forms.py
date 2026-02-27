from django import forms
from .models import Book, Author

class BookForm(forms.ModelForm):
    #Formulario para crear y editar libros ademas de validacion ISBM(International Standard Book Number)
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'is_available']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_isbn(self):
        """#Validacion ISBN
        Validación personalizada: ISBN debe tener 10 o 13 caracteres numéricos.
        Django llama automáticamente a los métodos clean_<campo>()
        """
        isbn = self.cleaned_data.get('isbn')       
        #Valida el tamaño del ISBN
        if len(isbn) not in [10, 13]:
            raise forms.ValidationError('El ISBN debe tener 10 o 13 dígitos.')
        
        #Valida que sean solo numeros
        if not isbn.isdigit():
            raise forms.ValidationError('El ISBN solo debe contener números (o guiones como separadores).')
        
        return isbn


class AuthorForm(forms.ModelForm):
    #Formulario para crear autores
    class Meta:
        model = Author
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
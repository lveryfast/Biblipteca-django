from django import forms
from django.contrib.auth.models import User
from catalog.models import Book
from .models import Loan


class LoanForm(forms.ModelForm):
    #Formulario para los prestamos
    class Meta:
        model = Loan
        fields = ['book', 'user', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Filtra los libros disponibles
        self.fields['book'].queryset = Book.objects.filter(is_available=True)
    
    def clean_book(self):
        #Validacion para NO permitir un prestamo si el libro no esta disponible
        book = self.cleaned_data.get('book')
        if not book.is_available:
            raise forms.ValidationError('Este libro ya está prestado.')
        return book


class LoanReturnForm(forms.Form):
    #Formulario para devolucion
    confirm = forms.BooleanField(required=True, label="Confirmar devolución")
from django.db import models

# Create your models here.
class Author(models.Model):
    # Modelo de los autores
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "authors"


class Book(models.Model):
    # Modelo de los libros
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=13, unique=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - {self.author.name}"
    
    def get_status_display(self):
        #Obtiene y muesta el estado del libro
        if self.is_available:
            return "Disponible"
        return "Prestado"
    
    def get_last_loan_date(self):
        #Obtiene la fecha del ultino prestamo del libro
        from loans.models import Loan
        last_loan = Loan.objects.filter(book=self).order_by('-start_date').first()
        if last_loan:
            return last_loan.start_date
        return None
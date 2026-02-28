from django.db import models
from django.contrib.auth.models import User
from catalog.models import Book

# Create your models here.
class Loan(models.Model):
    #Modelo de prestamos de libros
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)  #Fecha de inicio del prestamo
    due_date = models.DateField()  #Fecha de vencimiento
    end_date = models.DateField(null=True, blank=True)  #Fecha de devolución
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.book.title} - {self.user.username} ({self.start_date})"
    
    def is_overdue(self):
        #Verifica si el préstamo está vencido (solo para activos)
        from datetime import date
        if self.is_active and date.today() > self.due_date:
            return True
        return False
    
    class Meta:
        ordering = ['-start_date']


class Fine(models.Model):
    #Modelo para multas
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE)
    late_days = models.IntegerField()
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Multa: {self.loan.book.title} - ${self.fine_amount}"
    
    def calculate_fine(self):
        #calcula el monto de la multa dias * 1000
        return self.late_days * 1000
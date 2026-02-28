from django.contrib import admin
from .models import Loan, Fine

# Register your models here.
@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    #Muestra los campos, filtra y busca
    list_display = ['book', 'user', 'start_date', 'due_date', 'is_active']
    list_filter = ['is_active', 'start_date']
    search_fields = ['book__title', 'user__username']


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    #Muestra una lista
    list_display = ['loan', 'late_days', 'fine_amount']
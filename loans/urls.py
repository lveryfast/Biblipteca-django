from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    #Usuarios autenticados
    path('my-loans/', views.my_loans, name='my_loans'),
    
    #Staff
    path('', views.loan_list, name='loan_list'),
    path('create/', views.loan_create, name='loan_create'),
    path('<int:pk>/return/', views.loan_return, name='loan_return'),
    path('fines/', views.fine_list, name='fine_list'),
]
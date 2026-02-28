from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import date
from .models import Loan, Fine
from .forms import LoanForm, LoanReturnForm

# Create your views here.
def is_staff(user):
    #Verifica si es staff
    return user.is_staff


#Vista publica

@login_required
def my_loans(request):
    #Prestamos del usuario
    active_loans = Loan.objects.filter(user=request.user, is_active=True)
    past_loans = Loan.objects.filter(user=request.user, is_active=False)
    
    return render(request, 'loans/my_loans.html', {
        'active_loans': active_loans,
        'past_loans': past_loans,
    })


#Vista del staff
@login_required
@user_passes_test(is_staff)
def loan_create(request):
    #Crea nuevo libro
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            #Verifica la disponibilidad
            if not loan.book.is_available:
                messages.error(request, 'El libro ya no está disponible.')
                return render(request, 'loans/loan_form.html', {'form': form})
            
            #Guarda el prestamo 
            loan.save()
            loan.book.is_available = False
            loan.book.save()
            
            messages.success(request, f'Préstamo creado: {loan.book.title}')
            return redirect('loans:loan_list')
        messages.error(request, 'Corrige los errores.')
    else:
        form = LoanForm()
    
    return render(request, 'loans/loan_form.html', {'form': form})


@login_required
@user_passes_test(is_staff)
def loan_list(request):
    #Listado de prestamos
    loans = Loan.objects.select_related('book', 'user').all()
    return render(request, 'loans/loan_list.html', {'loans': loans})


@login_required
@user_passes_test(is_staff)
def loan_return(request, pk):
    #Devolucion del libro
    loan = get_object_or_404(Loan, pk=pk, is_active=True)
    
    if request.method == 'POST':
        form = LoanReturnForm(request.POST)
        if form.is_valid():
            #Fecha actual como fecha de devolucion
            loan.end_date = date.today()
            loan.is_active = False
            loan.save()
            
            #Marca el libro como disponible
            loan.book.is_available = True
            loan.book.save()
            
            #Verifica y crea la multa
            if loan.end_date > loan.due_date:
                late_days = (loan.end_date - loan.due_date).days
                fine_amount = late_days * 1000
                
                Fine.objects.create(
                    loan=loan,
                    late_days=late_days,
                    fine_amount=fine_amount
                )
                messages.warning(
                    request, 
                    f'Devolución con retraso: {late_days} días. Multa: ${fine_amount}'
                )
            else:
                messages.success(request, 'Devolución exitosa sin retraso.')
            
            return redirect('loans:loan_list')
    else:
        form = LoanReturnForm()
    
    return render(request, 'loans/loan_return.html', {
        'loan': loan,
        'form': form,
    })


@login_required
@user_passes_test(is_staff)
def fine_list(request):
    #Listado de multas
    fines = Fine.objects.select_related('loan__book', 'loan__user').all()
    return render(request, 'loans/fine_list.html', {'fines': fines})
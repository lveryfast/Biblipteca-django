from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from catalog.models import Author, Book
from .models import Loan, Fine

# Create your tests here.
class LoanFlowTests(TestCase):
    #test de prestamos(6 test)
    
    def setUp(self):
        self.client = Client()
        #Crea data base de prueba
        self.author = Author.objects.create(name='Test Author')
        self.book = Book.objects.create(
            title='Libro Test',
            author=self.author,
            isbn='8888888888888',
            is_available=True
        )
        #Users
        self.user = User.objects.create_user('prestamista', password='test123')
        self.staff = User.objects.create_user('bibliotecario', password='test123', is_staff=True)
    
    def test_prestar_cambia_estado(self):
        #test 18:Al prestar el libro pasa a no dispo
        self.client.login(username='bibliotecario', password='test123')
        
        #Verifica el estado inicial
        self.assertTrue(self.book.is_available)
        
        #Crea un prestamo
        response = self.client.post(reverse('loans:loan_create'), {
            'book': self.book.id,
            'user': self.user.id,
            'due_date': date.today() + timedelta(days=7)
        })
        
        #Verifica redireccion
        self.assertEqual(response.status_code, 302)
        
        #Verifica el cambio de estado
        self.book.refresh_from_db()
        self.assertFalse(self.book.is_available)
    
    def test_no_se_presta_dos_veces(self):
        #test 19:Libro no disponible luego de un prestamo
        self.book.is_available = False
        self.book.save()
        
        self.client.login(username='bibliotecario', password='test123')
        response = self.client.get(reverse('loans:loan_create'))
        
        #No tiene el libro disponible
        self.assertContains(response, '<select name="book"')
        self.assertNotContains(response, f'{self.book.title}')
    
    def test_devolver_reactiva_libro(self):
        #test 20:Al devolver, ya esta dispo
        self.client.login(username='bibliotecario', password='test123')
        
        #Crea un prestamo
        loan = Loan.objects.create(
            book=self.book,
            user=self.user,
            due_date=date.today() + timedelta(days=7),
            is_active=True
        )
        self.book.is_available = False
        self.book.save()
        
        #Devuelve
        response = self.client.post(
            reverse('loans:loan_return', kwargs={'pk': loan.pk}),
            {'confirm': True}
        )
        
        #Verifica redireccion
        self.assertEqual(response.status_code, 302)
        
        #Verifica la dispponibilidad del libro
        self.book.refresh_from_db()
        self.assertTrue(self.book.is_available)
        
        #Verifica el prestamo
        loan.refresh_from_db()
        self.assertFalse(loan.is_active)
        self.assertIsNotNone(loan.end_date)
    
    def test_devolver_con_retraso_crea_multa(self):
        #test 21:Devolucion tardia genera multa diaria
        self.client.login(username='bibliotecario', password='test123')
        
        #Prestamo vencido (5 dias)
        loan = Loan.objects.create(
            book=self.book,
            user=self.user,
            due_date=date.today() - timedelta(days=5),
            is_active=True
        )
        self.book.is_available = False
        self.book.save()
        
        #Verifica que no hay multas
        self.assertEqual(Fine.objects.count(), 0)
        
        #Devuelve el libro
        self.client.post(
            reverse('loans:loan_return', kwargs={'pk': loan.pk}),
            {'confirm': True}
        )
        
        #Verifica la multa
        self.assertEqual(Fine.objects.count(), 1)
        fine = Fine.objects.first()
        self.assertEqual(fine.late_days, 5)
        self.assertEqual(fine.fine_amount, 5000)
    
    def test_calculo_multa_correcto(self):
        #test 22:Buen calculo de la multa
        loan = Loan.objects.create(
            book=self.book,
            user=self.user,
            due_date=date.today() - timedelta(days=10),
            is_active=True
        )
        
        fine = Fine.objects.create(
            loan=loan,
            late_days=10,
            fine_amount=10000
        )
        
        self.assertEqual(fine.calculate_fine(), 10000)
        self.assertEqual(fine.late_days, 10)
    
    def test_prestamo_activo_en_mis_prestamos(self):
        #test 23:User ve sus prestamos
        self.client.login(username='prestamista', password='test123')
        
        #Crea un prestamo
        Loan.objects.create(
            book=self.book,
            user=self.user,
            due_date=date.today() + timedelta(days=7),
            is_active=True
        )
        
        response = self.client.get(reverse('loans:my_loans'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Libro Test')
        self.assertContains(response, 'Activos')


class LoanPermissionTests(TestCase):
    #test de permisos de prestamos
    
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(name='Test')
        self.book = Book.objects.create(
            title='Libro',
            author=self.author,
            isbn='9999999999999',
            is_available=True
        )
        self.user = User.objects.create_user('normal', password='test123')
        self.staff = User.objects.create_user('admin', password='test123', is_staff=True)
    
    def test_usuario_no_puede_crear_prestamo(self):
        #test 24:User auth no crea prestamos
        self.client.login(username='normal', password='test123')
        response = self.client.get(reverse('loans:loan_create'))
        self.assertEqual(response.status_code, 302)
    
    def test_visitante_no_ve_mis_prestamos(self):
        #test 25:Visitante no ve los prestamos
        response = self.client.get(reverse('loans:my_loans'))
        self.assertEqual(response.status_code, 302)
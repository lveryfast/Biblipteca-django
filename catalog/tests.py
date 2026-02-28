from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Author, Book
from .forms import BookForm

# Create your tests here.
class ModelTests(TestCase):
    #test de modelos (6 test)
    
    def setUp(self):
        #Configuracion para cada test
        self.author = Author.objects.create(name='Gabriel García Márquez')
    
    def test_creacion_autor(self):
        #test 1:Validacion de creacion de autor
        self.assertEqual(self.author.name, 'Gabriel García Márquez')
        self.assertEqual(str(self.author), 'Gabriel García Márquez')
    
    def test_creacion_libro(self):
        #test 2:Creacion del libro con relacion al author
        book = Book.objects.create(
            title='Cien años de soledad',
            author=self.author,
            isbn='1234567890123',
            is_available=True
        )
        self.assertEqual(book.title, 'Cien años de soledad')
        self.assertEqual(book.author, self.author)
        self.assertTrue(book.is_available)
    
    def test_isbn_unico(self):
        #test 3:ISBN unico
        Book.objects.create(
            title='Libro 1',
            author=self.author,
            isbn='9999999999999',
            is_available=True
        )
        #intenta crear un ISBN igual
        with self.assertRaises(Exception):
            Book.objects.create(
                title='Libro 2',
                author=self.author,
                isbn='9999999999999',
                is_available=True
            )
    
    def test_str_book(self):
        #test 4:str del libro
        book = Book.objects.create(
            title='El amor en los tiempos del cólera',
            author=self.author,
            isbn='1111111111111',
            is_available=True
        )
        self.assertEqual(str(book), 'El amor en los tiempos del cólera - Gabriel García Márquez')
    
    def test_get_status(self):
        #test 5:Estado de disponibilidad 
        book = Book.objects.create(
            title='Test',
            author=self.author,
            isbn='2222222222222',
            is_available=True
        )
        self.assertEqual(book.get_status_display(), 'Disponible')
    
    def test_get_status_prestado(self):
        #test 6:Prestado
        book = Book.objects.create(
            title='Test',
            author=self.author,
            isbn='3333333333333',
            is_available=False
        )
        self.assertEqual(book.get_status_display(), 'Prestado')


class FormTests(TestCase):
    #test de formularios
    
    def setUp(self):
        self.author = Author.objects.create(name='Test Author')
    
    def test_isbn_invalido_letras(self):
        #test 7:ISBN sin letras
        form_data = {
            'title': 'Libro Test',
            'author': self.author.id,
            'isbn': 'abc123',
            'is_available': True
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('isbn', form.errors)
    
    def test_isbn_invalido_longitud(self):
        #test 8:ISBN con longitud invalida
        form_data = {
            'title': 'Libro Test',
            'author': self.author.id,
            'isbn': '12345',
            'is_available': True
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('isbn', form.errors)


class ViewPublicTests(TestCase):
    #test de vistas (4 test)
    
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(name='Borges')
        self.book = Book.objects.create(
            title='Ficciones',
            author=self.author,
            isbn='4444444444444',
            is_available=True
        )
    
    def test_catalogo(self):
        #test 9:Catalogo
        response = self.client.get(reverse('catalog:book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ficciones')
    
    def test_detalle(self):
        #test 10:Detalle del libro
        response = self.client.get(
            reverse('catalog:book_detail', kwargs={'pk': self.book.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ficciones')
        self.assertContains(response, 'Borges')
    
    def test_busqueda_titulo(self):
        #test 11:Busca por titulo
        #Crea otro libro
        Book.objects.create(
            title='Otro libro',
            author=self.author,
            isbn='5555555555555',
            is_available=True
        )
        response = self.client.get(reverse('catalog:book_list'), {'q': 'Ficciones'})
        self.assertContains(response, 'Ficciones')
        self.assertNotContains(response, 'Otro libro')
    
    def test_busqueda_autor(self):
        #Test 12:Busca por author
        otro_autor = Author.objects.create(name='Otro Autor')
        Book.objects.create(
            title='Libro X',
            author=otro_autor,
            isbn='6666666666666',
            is_available=True
        )
        response = self.client.get(reverse('catalog:book_list'), {'q': 'Borges'})
        self.assertContains(response, 'Ficciones')
        self.assertNotContains(response, 'Libro X')


class AccessControlTests(TestCase):
    #test de control (5 test)
    
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(name='Test')
        self.book = Book.objects.create(
            title='Libro Test',
            author=self.author,
            isbn='7777777777777',
            is_available=True
        )
        #User
        self.user_normal = User.objects.create_user('usuario', password='test123')
        self.user_staff = User.objects.create_user('staff', password='test123', is_staff=True)
    
    def test_visitante_bloqueado_crud(self):
        #test 13:Visitante no puede hacer crud
        response = self.client.get(reverse('catalog:book_create'))
        self.assertIn(response.status_code, [302, 403, 200])
        if response.status_code == 200:
            self.assertContains(response, 'login')
    
    def test_autenticado_bloqueado_crud(self):
        #test 14:User autenticado no puede hacer crud
        self.client.login(username='usuario', password='test123')
        response = self.client.get(reverse('catalog:book_create'))
        self.assertEqual(response.status_code, 403)
    
    def test_staff_permitido_crear(self):
        #test 15:Staff puede crear libros
        self.client.login(username='staff', password='test123')
        response = self.client.get(reverse('catalog:book_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crear')
    
    def test_staff_permitido_editar(self):
        #test 16:Staff puede editar libros
        self.client.login(username='staff', password='test123')
        response = self.client.get(
            reverse('catalog:book_update', kwargs={'pk': self.book.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editar')
    
    def test_staff_permitido_eliminar(self):
        #test 17:Staff puede eliminar libros
        self.client.login(username='staff', password='test123')
        response = self.client.get(
            reverse('catalog:book_delete', kwargs={'pk': self.book.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eliminar')
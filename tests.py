import unittest
from app import app, db
from models import User, Tender
from flask_login import current_user
import json

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            # Создаем тестового пользователя
            user = User(
                email='test@example.com',
                last_name='Test',
                first_name='User',
                phone='+79991234567',
                company_name='Test Company'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_page(self):
        """Тест главной страницы"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'OpenTender', response.data)

    def test_register_page(self):
        """Тест страницы регистрации"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_login_page(self):
        """Тест страницы входа"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_about_page(self):
        """Тест страницы о нас"""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About', response.data)

    def test_tenders_page(self):
        """Тест страницы закупок"""
        response = self.client.get('/tenders')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tenders', response.data)

    def test_terms_page(self):
        """Тест страницы условий использования"""
        response = self.client.get('/terms')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Terms', response.data)

    def test_privacy_page(self):
        """Тест страницы конфиденциальности"""
        response = self.client.get('/privacy')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Privacy', response.data)

    def test_register_api(self):
        """Тест API регистрации"""
        data = {
            'email': 'new@example.com',
            'password': 'password123',
            'last_name': 'New',
            'first_name': 'User',
            'phone': '+79991234568',
            'company_name': 'New Company'
        }
        response = self.client.post('/api/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Registration successful', response.data)

    def test_login_api(self):
        """Тест API входа"""
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post('/api/login',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful', response.data)

    def test_profile_api(self):
        """Тест API профиля"""
        # Сначала логинимся
        self.client.post('/api/login',
                        data=json.dumps({
                            'email': 'test@example.com',
                            'password': 'password123'
                        }),
                        content_type='application/json')
        
        # Получаем профиль
        response = self.client.get('/api/profile')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['email'], 'test@example.com')

    def test_update_profile_api(self):
        """Тест API обновления профиля"""
        # Сначала логинимся
        self.client.post('/api/login',
                        data=json.dumps({
                            'email': 'test@example.com',
                            'password': 'password123'
                        }),
                        content_type='application/json')
        
        # Обновляем профиль
        data = {
            'first_name': 'Updated',
            'last_name': 'User'
        }
        response = self.client.put('/api/profile',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile updated successfully', response.data)

    def test_logout(self):
        """Тест выхода из системы"""
        # Сначала логинимся
        self.client.post('/api/login',
                        data=json.dumps({
                            'email': 'test@example.com',
                            'password': 'password123'
                        }),
                        content_type='application/json')
        
        # Выходим
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)  # Редирект на главную

    def test_invalid_login(self):
        """Тест неверного входа"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/login',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid email or password', response.data)

    def test_duplicate_registration(self):
        """Тест повторной регистрации"""
        data = {
            'email': 'test@example.com',  # Email уже существует
            'password': 'password123',
            'last_name': 'Test',
            'first_name': 'User',
            'phone': '+79991234567',
            'company_name': 'Test Company'
        }
        response = self.client.post('/api/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'User with this email already exists', response.data)

if __name__ == '__main__':
    unittest.main() 
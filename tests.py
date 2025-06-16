import unittest
from app import app, db
from models import User, Tender
from flask_login import current_user, login_user
import json
from unittest.mock import patch, MagicMock

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

class TestOAuth(unittest.TestCase):
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
                password_hash='test_hash',
                first_name='Test',
                last_name='User',
                phone='+79001234567',
                company_name='Test Company'
            )
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_oauth_providers_list(self):
        """Тест доступности списка OAuth провайдеров"""
        response = self.client.get('/oauth/vk')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('oauth.vk.com' in response.location)

        response = self.client.get('/oauth/yandex')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('oauth.yandex.ru' in response.location)

        response = self.client.get('/oauth/google')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('accounts.google.com' in response.location)

    @patch('requests.get')
    @patch('requests.post')
    def test_vk_oauth_callback(self, mock_post, mock_get):
        """Тест callback для VK OAuth"""
        # Мокаем ответы от VK API
        mock_post.return_value.json.return_value = {
            'access_token': 'test_token',
            'email': 'test@vk.com'
        }
        mock_get.return_value.json.return_value = {
            'response': [{
                'id': 12345,
                'first_name': 'VK',
                'last_name': 'User'
            }]
        }

        response = self.client.get('/oauth/vk/callback?code=test_code')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

        # Проверяем, что пользователь создан
        with app.app_context():
            user = User.query.filter_by(social_id='12345').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@vk.com')
            self.assertEqual(user.first_name, 'VK')
            self.assertEqual(user.last_name, 'User')

    @patch('requests.get')
    @patch('requests.post')
    def test_yandex_oauth_callback(self, mock_post, mock_get):
        """Тест callback для Yandex OAuth"""
        # Мокаем ответы от Yandex API
        mock_post.return_value.json.return_value = {
            'access_token': 'test_token'
        }
        mock_get.return_value.json.return_value = {
            'id': '12345',
            'default_email': 'test@yandex.ru',
            'first_name': 'Yandex',
            'last_name': 'User'
        }

        response = self.client.get('/oauth/yandex/callback?code=test_code')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

        # Проверяем, что пользователь создан
        with app.app_context():
            user = User.query.filter_by(social_id='12345').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@yandex.ru')
            self.assertEqual(user.first_name, 'Yandex')
            self.assertEqual(user.last_name, 'User')

    @patch('requests.get')
    @patch('requests.post')
    def test_google_oauth_callback(self, mock_post, mock_get):
        """Тест callback для Google OAuth"""
        # Мокаем ответы от Google API
        mock_post.return_value.json.return_value = {
            'access_token': 'test_token'
        }
        mock_get.return_value.json.return_value = {
            'id': '12345',
            'email': 'test@gmail.com',
            'given_name': 'Google',
            'family_name': 'User'
        }

        response = self.client.get('/oauth/google/callback?code=test_code')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

        # Проверяем, что пользователь создан
        with app.app_context():
            user = User.query.filter_by(social_id='12345').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@gmail.com')
            self.assertEqual(user.first_name, 'Google')
            self.assertEqual(user.last_name, 'User')

    def test_invalid_oauth_provider(self):
        """Тест обработки неверного OAuth провайдера"""
        response = self.client.get('/oauth/invalid')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Неподдерживаемый провайдер')

    def test_oauth_callback_without_code(self):
        """Тест callback без кода авторизации"""
        response = self.client.get('/oauth/vk/callback')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Код авторизации отсутствует')

if __name__ == '__main__':
    unittest.main() 
from flask import jsonify, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps
from extensions import db, limiter
from models import User, Tender, TenderHistory
from config import Config
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_login import login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from urllib.parse import urlencode

limiter = Limiter(key_func=get_remote_address)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Токен отсутствует'}), 401
        try:
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'error': 'Недействительный токен'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def register_routes(app):
    limiter.init_app(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/tenders')
    def tenders():
        return render_template('tenders.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/login')
    def login():
        return render_template('login.html')

    @app.route('/register')
    def register():
        return render_template('register.html')

    @app.route('/terms')
    def terms():
        return render_template('terms.html')

    @app.route('/privacy')
    def privacy():
        return render_template('privacy.html')

    @app.route('/api/register', methods=['POST'])
    @limiter.limit("5 per minute")
    def register_api():
        data = request.get_json()
        
        # Проверка обязательных полей
        required_fields = ['email', 'password', 'last_name', 'first_name', 'phone', 'company_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Поле {field} обязательно для заполнения'}), 400
        
        # Проверка существования пользователя
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Пользователь с таким email уже существует'}), 400
        
        # Проверка пароля
        if not User.validate_password(data['password']):
            return jsonify({'error': 'Пароль не соответствует требованиям безопасности'}), 400
        
        # Создание пользователя
        user = User(
            email=data['email'],
            last_name=data['last_name'],
            first_name=data['first_name'],
            middle_name=data.get('middle_name'),
            phone=data['phone'],
            company_name=data['company_name']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Автоматический вход после регистрации
        login_user(user)
        
        # Создание токена
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Регистрация успешна',
            'access_token': access_token
        }), 201

    @app.route('/api/login', methods=['POST'])
    @limiter.limit("5 per minute")
    def login_api():
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Необходимо указать email и пароль'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Неверный email или пароль'}), 401
        
        # Вход пользователя
        login_user(user)
        
        # Создание токена
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Вход выполнен успешно',
            'access_token': access_token
        }), 200

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/api/profile', methods=['GET'])
    @login_required
    def get_profile():
        return jsonify({
            'id': current_user.id,
            'email': current_user.email,
            'last_name': current_user.last_name,
            'first_name': current_user.first_name,
            'middle_name': current_user.middle_name,
            'phone': current_user.phone,
            'company_name': current_user.company_name
        })

    @app.route('/api/profile', methods=['PUT'])
    @login_required
    def update_profile():
        data = request.get_json()
        
        if 'email' in data and data['email'] != current_user.email:
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Пользователь с таким email уже существует'}), 400
            current_user.email = data['email']
            
        if 'last_name' in data:
            current_user.last_name = data['last_name']
        if 'first_name' in data:
            current_user.first_name = data['first_name']
        if 'middle_name' in data:
            current_user.middle_name = data['middle_name']
        if 'phone' in data:
            current_user.phone = data['phone']
        if 'company_name' in data:
            current_user.company_name = data['company_name']
            
        if 'password' in data:
            if not User.validate_password(data['password']):
                return jsonify({'error': 'Пароль не соответствует требованиям безопасности'}), 400
            current_user.set_password(data['password'])
            
        try:
            db.session.commit()
            return jsonify({
                'message': 'Профиль успешно обновлен',
                'user': {
                    'id': current_user.id,
                    'email': current_user.email,
                    'last_name': current_user.last_name,
                    'first_name': current_user.first_name,
                    'middle_name': current_user.middle_name,
                    'phone': current_user.phone,
                    'company_name': current_user.company_name
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Ошибка при обновлении профиля'}), 500

    @app.route('/api/change-password', methods=['POST'])
    @token_required
    def change_password(current_user):
        data = request.get_json()
        
        if not current_user.check_password(data['current_password']):
            return jsonify({'message': 'Неверный текущий пароль'}), 400
            
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Пароль успешно изменен'})

    @app.route('/api/tenders', methods=['GET'])
    def get_tenders():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        status = request.args.get('status')
        search = request.args.get('search')
        
        query = Tender.query
        
        if category:
            query = query.filter_by(category=category)
        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(Tender.title.ilike(f'%{search}%'))
            
        pagination = query.order_by(Tender.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'tenders': [{
                'id': tender.id,
                'title': tender.title,
                'description': tender.description,
                'initial_price': tender.initial_price,
                'category': tender.category,
                'status': tender.status,
                'submission_deadline': tender.submission_deadline.isoformat(),
                'created_at': tender.created_at.isoformat()
            } for tender in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })

    @app.route('/api/tenders/<int:tender_id>', methods=['GET'])
    def get_tender(tender_id):
        tender = Tender.query.get_or_404(tender_id)
        return jsonify({
            'id': tender.id,
            'title': tender.title,
            'description': tender.description,
            'initial_price': tender.initial_price,
            'category': tender.category,
            'status': tender.status,
            'submission_deadline': tender.submission_deadline.isoformat(),
            'created_at': tender.created_at.isoformat(),
            'history': [{
                'field': h.field,
                'old_value': h.old_value,
                'new_value': h.new_value,
                'changed_at': h.changed_at.isoformat()
            } for h in tender.history]
        })

    @app.route('/api/dashboard', methods=['GET'])
    @token_required
    def get_dashboard(current_user):
        total_tenders = Tender.query.count()
        active_tenders = Tender.query.filter_by(status='active').count()
        total_value = db.session.query(db.func.sum(Tender.initial_price)).scalar() or 0
        
        categories = db.session.query(
            Tender.category,
            db.func.count(Tender.id)
        ).group_by(Tender.category).all()
        
        return jsonify({
            'statistics': {
                'total_tenders': total_tenders,
                'active_tenders': active_tenders,
                'total_value': total_value
            },
            'categories': [{
                'name': category,
                'count': count
            } for category, count in categories]
        })

    @app.route('/oauth/<provider>')
    def oauth_authorize(provider):
        if provider not in ['vk', 'yandex', 'google']:
            return jsonify({'error': 'Неподдерживаемый провайдер'}), 400

        oauth_config = app.config['OAUTH_CREDENTIALS'][provider]
        
        if provider == 'vk':
            params = {
                'client_id': oauth_config['id'],
                'redirect_uri': url_for('oauth_callback', provider=provider, _external=True),
                'response_type': 'code',
                'scope': 'email'
            }
            return redirect(f'https://oauth.vk.com/authorize?{urlencode(params)}')
        
        elif provider == 'yandex':
            params = {
                'client_id': oauth_config['id'],
                'redirect_uri': url_for('oauth_callback', provider=provider, _external=True),
                'response_type': 'code'
            }
            return redirect(f'https://oauth.yandex.ru/authorize?{urlencode(params)}')
        
        elif provider == 'google':
            params = {
                'client_id': oauth_config['id'],
                'redirect_uri': url_for('oauth_callback', provider=provider, _external=True),
                'response_type': 'code',
                'scope': 'email profile'
            }
            return redirect(f'https://accounts.google.com/o/oauth2/auth?{urlencode(params)}')

    @app.route('/oauth/<provider>/callback')
    def oauth_callback(provider):
        if provider not in ['vk', 'yandex', 'google']:
            return jsonify({'error': 'Неподдерживаемый провайдер'}), 400

        oauth_config = app.config['OAUTH_CREDENTIALS'][provider]
        code = request.args.get('code')
        
        if not code:
            return jsonify({'error': 'Код авторизации отсутствует'}), 400

        if provider == 'vk':
            # Получаем токен
            token_url = 'https://oauth.vk.com/access_token'
            token_params = {
                'client_id': oauth_config['id'],
                'client_secret': oauth_config['secret'],
                'redirect_uri': url_for('oauth_callback', provider=provider, _external=True),
                'code': code
            }
            token_response = requests.get(token_url, params=token_params)
            token_data = token_response.json()
            
            if 'error' in token_data:
                return jsonify({'error': 'Ошибка получения токена'}), 400
            
            # Получаем информацию о пользователе
            user_url = 'https://api.vk.com/method/users.get'
            user_params = {
                'access_token': token_data['access_token'],
                'v': '5.131',
                'fields': 'email'
            }
            user_response = requests.get(user_url, params=user_params)
            user_data = user_response.json()['response'][0]
            
            user = User.get_or_create_social_user(
                social_id=str(user_data['id']),
                social_provider='vk',
                email=token_data.get('email', ''),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', '')
            )
            
        elif provider == 'yandex':
            # Получаем токен
            token_url = 'https://oauth.yandex.ru/token'
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': oauth_config['id'],
                'client_secret': oauth_config['secret']
            }
            token_response = requests.post(token_url, data=token_data)
            token_info = token_response.json()
            
            if 'error' in token_info:
                return jsonify({'error': 'Ошибка получения токена'}), 400
            
            # Получаем информацию о пользователе
            user_url = 'https://login.yandex.ru/info'
            user_response = requests.get(user_url, headers={'Authorization': f'OAuth {token_info["access_token"]}'})
            user_data = user_response.json()
            
            user = User.get_or_create_social_user(
                social_id=user_data['id'],
                social_provider='yandex',
                email=user_data.get('default_email', ''),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', '')
            )
            
        elif provider == 'google':
            # Получаем токен
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'client_id': oauth_config['id'],
                'client_secret': oauth_config['secret'],
                'redirect_uri': url_for('oauth_callback', provider=provider, _external=True),
                'grant_type': 'authorization_code',
                'code': code
            }
            token_response = requests.post(token_url, data=token_data)
            token_info = token_response.json()
            
            if 'error' in token_info:
                return jsonify({'error': 'Ошибка получения токена'}), 400
            
            # Получаем информацию о пользователе
            user_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
            user_response = requests.get(user_url, headers={'Authorization': f'Bearer {token_info["access_token"]}'})
            user_data = user_response.json()
            
            user = User.get_or_create_social_user(
                social_id=user_data['id'],
                social_provider='google',
                email=user_data.get('email', ''),
                first_name=user_data.get('given_name', ''),
                last_name=user_data.get('family_name', '')
            )

        login_user(user)
        return redirect(url_for('index')) 
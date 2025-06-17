from flask import jsonify, request, render_template, redirect, url_for, session, abort, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps
from extensions import db, limiter
from models import User, Tender, TenderHistory, Analysis, Document, Milestone, Anomaly, Alert, ContractStatus, UserRole
from config import Config
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_login import login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from urllib.parse import urlencode
import json
import os

limiter = Limiter(key_func=get_remote_address)

def token_required(f):
    """Декоратор для проверки JWT токена"""
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

def role_required(roles):
    """Декоратор для проверки роли пользователя"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.role or current_user.role.name not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def register_routes(app):
    """
    Регистрация маршрутов приложения
    
    OpenTender - инновационная ИИ-платформа для автоматизированного контроля 
    исполнения государственных контрактов в РФ
    """
    limiter.init_app(app)

    @app.route('/')
    def index():
        """Главная страница системы"""
        return render_template('index.html')

    @app.route('/tenders')
    def tenders():
        """Страница со списком тендеров"""
        return render_template('tenders.html')
        
    @app.route('/monitoring')
    @login_required
    def monitoring():
        """Страница мониторинга исполнения контрактов"""
        return render_template('monitoring.html')
        
    @app.route('/analytics')
    @login_required
    def analytics():
        """Страница аналитики и отчетов"""
        return render_template('analytics.html')

    @app.route('/about')
    def about():
        """Страница о проекте"""
        return render_template('about.html')

    @app.route('/login')
    def login():
        """Страница входа"""
        return render_template('login.html')

    @app.route('/register')
    def register():
        """Страница регистрации"""
        return render_template('register.html')

    @app.route('/terms')
    def terms():
        """Условия использования"""
        return render_template('terms.html')

    @app.route('/privacy')
    def privacy():
        """Политика конфиденциальности"""
        return render_template('privacy.html')
        
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Панель управления пользователя"""
        return render_template('dashboard.html')
        
    @app.route('/chat')
    def chat():
        """Страница чата с ИИ"""
        return render_template('chat.html')

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

    return app  # Возвращаем настроенное приложение
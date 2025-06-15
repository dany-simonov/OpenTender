from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from datetime import timedelta
import os
from config import Config

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)

    # Конфигурация
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///opentender.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

    # OAuth конфигурация
    app.config['OAUTH_CREDENTIALS'] = {
        'vk': {
            'id': os.getenv('VK_APP_ID'),
            'secret': os.getenv('VK_APP_SECRET')
        },
        'yandex': {
            'id': os.getenv('YANDEX_APP_ID'),
            'secret': os.getenv('YANDEX_APP_SECRET')
        },
        'google': {
            'id': os.getenv('GOOGLE_APP_ID'),
            'secret': os.getenv('GOOGLE_APP_SECRET')
        }
    }

    # Инициализация расширений с приложением
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Регистрация маршрутов
    from routes import register_routes
    register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
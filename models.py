from app import db
from datetime import datetime
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    phone = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # OAuth поля
    social_id = db.Column(db.String(100), unique=True)
    social_provider = db.Column(db.String(20))  # 'vk', 'yandex', 'google'
    social_token = db.Column(db.String(200))
    social_token_expires = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_password(password):
        """
        Проверяет соответствие пароля требованиям безопасности:
        - Минимум 8 символов
        - Минимум одна заглавная буква
        - Минимум одна строчная буква
        - Минимум одна цифра
        - Минимум один специальный символ
        """
        if len(password) < 8:
            return False
        
        if not re.search(r'[A-Z]', password):
            return False
            
        if not re.search(r'[a-z]', password):
            return False
            
        if not re.search(r'\d', password):
            return False
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
            
        return True

    @staticmethod
    def get_or_create_social_user(social_id, social_provider, email, first_name, last_name):
        user = User.query.filter_by(social_id=social_id, social_provider=social_provider).first()
        if not user:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                social_id=social_id,
                social_provider=social_provider,
                phone='',  # Можно запросить позже
                company_name=''  # Можно запросить позже
            )
            db.session.add(user)
            db.session.commit()
        return user

    def __repr__(self):
        return f'<User {self.email}>'

class Tender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    customer = db.Column(db.String(200))
    price = db.Column(db.Float)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Tender {self.title}>'

class TenderHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey('tender.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    tender = db.relationship('Tender', backref=db.backref('history', lazy=True))
    user = db.relationship('User', backref=db.backref('tender_history', lazy=True))

    def __repr__(self):
        return f'<TenderHistory {self.action}>'

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey('tender.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    technical_analysis = db.Column(db.Text)
    budget_analysis = db.Column(db.Text)
    risk_analysis = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tender = db.relationship('Tender', backref=db.backref('analyses', lazy=True))
    user = db.relationship('User', backref=db.backref('analyses', lazy=True)) 
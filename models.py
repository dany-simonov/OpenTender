from app import db
from datetime import datetime
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum

class UserRole(enum.Enum):
    USER = "user"
    ANALYST = "analyst"
    AUDITOR = "auditor"
    ADMIN = "admin"

class User(UserMixin, db.Model):
    """
    Модель пользователя системы OpenTender
    
    Поддерживает как стандартную аутентификацию, так и OAuth через
    российские платформы VK ID, Яндекс ID и международный стандарт Google OAuth
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    phone = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # OAuth поля
    social_id = db.Column(db.String(100), unique=True)
    social_provider = db.Column(db.String(20))  # 'vk', 'yandex', 'google'
    social_token = db.Column(db.String(200))
    social_token_expires = db.Column(db.DateTime)

    # Отношения
    analyses = db.relationship('Analysis', backref='analyst', lazy='dynamic')
    alerts = db.relationship('Alert', backref='user', lazy='dynamic')
    
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

class ContractStatus(enum.Enum):
    """Статусы государственных контрактов"""
    DRAFT = "draft"                # Черновик
    PUBLISHED = "published"        # Опубликован
    BIDDING = "bidding"            # Идет прием заявок
    EVALUATION = "evaluation"      # Оценка заявок
    AWARDED = "awarded"            # Определен победитель
    SIGNED = "signed"              # Контракт подписан
    IN_PROGRESS = "in_progress"    # В процессе исполнения
    COMPLETED = "completed"        # Исполнен
    TERMINATED = "terminated"      # Расторгнут
    SUSPENDED = "suspended"        # Приостановлен

class Tender(db.Model):
    """
    Модель государственного тендера/контракта
    
    Содержит основную информацию о государственном контракте,
    включая дан��ые о заказчике, поставщике, сроках и стоимости
    """
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.String(50), unique=True, nullable=False, comment="Уникальный ID тендера в ЕИС")
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    customer = db.Column(db.String(200), nullable=False, comment="Наименование заказчика")
    customer_inn = db.Column(db.String(12), comment="ИНН заказчика")
    supplier = db.Column(db.String(200), comment="Наименование поставщика")
    supplier_inn = db.Column(db.String(12), comment="ИНН поставщика")
    price = db.Column(db.Float, comment="Цена контракта")
    initial_price = db.Column(db.Float, comment="Начальная (максимальная) цена контракта")
    category = db.Column(db.String(100), comment="Категория закупки")
    status = db.Column(db.Enum(ContractStatus), default=ContractStatus.PUBLISHED)
    publication_date = db.Column(db.DateTime, comment="Дата публикации")
    submission_deadline = db.Column(db.DateTime, comment="Срок подачи заявок")
    execution_deadline = db.Column(db.DateTime, comment="Срок исполнения контракта")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Отношения
    history = db.relationship('TenderHistory', backref='tender', lazy='dynamic', cascade="all, delete-orphan")
    analyses = db.relationship('Analysis', backref='tender', lazy='dynamic', cascade="all, delete-orphan")
    documents = db.relationship('Document', backref='tender', lazy='dynamic', cascade="all, delete-orphan")
    milestones = db.relationship('Milestone', backref='tender', lazy='dynamic', cascade="all, delete-orphan")
    anomalies = db.relationship('Anomaly', backref='tender', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Tender {self.tender_id}: {self.title}>'

class TenderHistory(db.Model):
    """
    История изменений тендера
    
    Отслеживает все изменения в данных о тендере для обесп��чения
    прозрачности и аудита
    """
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey('tender.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    field = db.Column(db.String(50), nullable=False, comment="Измененное поле")
    old_value = db.Column(db.Text, comment="Предыдущее значение")
    new_value = db.Column(db.Text, comment="Новое значение")
    changed_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    source = db.Column(db.String(50), comment="Источник изменения (ЕИС, пользователь, система)")

    # Отношения
    user = db.relationship('User', backref=db.backref('changes', lazy='dynamic'))

    def __repr__(self):
        return f'<TenderHistory {self.field}: {self.old_value} -> {self.new_value}>'

class Analysis(db.Model):
    """
    Результаты анализа тендера
    
    Содержит результаты автоматического анализа тендера с использованием
    искусственного интеллекта по различным аспектам
    """
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey('tender.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    technical_analysis = db.Column(db.Text, comment="Анализ технического задания")
    budget_analysis = db.Column(db.Text, comment="Анализ бюджета и ценообразования")
    risk_analysis = db.Column(db.Text, comment="Анализ рисков")
    compliance_analysis = db.Column(db.Text, comment="Анализ соответствия требованиям")
    recommendations = db.Column(db.Text, comment="Рекомендации")
    risk_score = db.Column(db.Float, comment="Оценка риска (0-100)")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_confidential = db.Column(db.Boolean, default=False, comment="Флаг конфиденциального анализа")

    def __repr__(self):
        return f'<Analysis {self.id} for Tender {self.tender_id}>'

class Document(db.Model):
    """
    Документы, связанные с тендером
    
    Хранит информацию о документах тендера для анализа
    """
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey('tender.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50), comment="Тип документа")
    file_path = db.Column(db.String(500), comment="Путь к файлу")
    content = db.Column(db.Text, comment="Извлеченное содержимое документа")
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_analyzed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Document {self.title}>'

class Milestone(db.Model):
    """
    Этапы исполнения контракта
    
    Отслеживает ключевые этапы исполнения государственного контракта
    """
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey('tender.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    completion_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default="pending")
    amount = db.Column(db.Float, comment="Сумма этапа")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Milestone {self.title}>'

class Anomaly(db.Model):
    """
    Выявленные аномалии в тендере
    
    Хранит информацию о выявленных системой аномалиях и нарушениях
    в процессе исполнения контракта
    """
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey('tender.id'), nullable=False)
    anomaly_type = db.Column(db.String(50), nullable=False, comment="Тип аномалии")
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default="medium", comment="Серьезность: low, medium, high, critical")
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="open", comment="Статус: open, investigating, resolved, false_positive")
    resolution_notes = db.Column(db.Text)

    def __repr__(self):
        return f'<Anomaly {self.anomaly_type}: {self.severity}>'

class Alert(db.Model):
    """
    Уведомления для пользователей
    
    Система оповещений о важных событиях, аномалиях и сроках
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tender_id = db.Column(db.Integer, db.ForeignKey('tender.id'))
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.String(50), default="info", comment="Тип: info, warning, danger")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)

    # Отношения
    tender = db.relationship('Tender', backref=db.backref('alerts', lazy='dynamic'))

    def __repr__(self):
        return f'<Alert {self.title}>'
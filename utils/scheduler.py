from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging
from models import Tender, db
from .parser import TenderParser
from .analyzer import TenderAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenderScheduler:
    """
    Планировщик задач для автоматического мониторинга и анализа тендеров
    
    Обеспечивает непрерывный контроль качества исполнения обязательств поставщиками
    через регулярное обновление данных и выявление аномалий в исполнении контрактов.
    """
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.parser = TenderParser()
        self.analyzer = TenderAnalyzer()
        self.setup_jobs()

    def setup_jobs(self):
        """Настройка периодических задач мониторинга"""
        # Обновление данных о тендерах каждый час
        self.scheduler.add_job(
            self.update_tenders,
            trigger=IntervalTrigger(hours=1),
            id='update_tenders',
            name='Update tenders data',
            replace_existing=True
        )

        # Очистка старых тендеров раз в день
        self.scheduler.add_job(
            self.cleanup_old_tenders,
            trigger=IntervalTrigger(days=1),
            id='cleanup_tenders',
            name='Cleanup old tenders',
            replace_existing=True
        )
        
        # Анализ аномалий в исполнении контрактов
        self.scheduler.add_job(
            self.analyze_contract_anomalies,
            trigger=IntervalTrigger(hours=4),
            id='analyze_anomalies',
            name='Analyze contract anomalies',
            replace_existing=True
        )
        
        # Проверка сроков исполнения контрактов
        self.scheduler.add_job(
            self.check_contract_deadlines,
            trigger=IntervalTrigger(hours=6),
            id='check_deadlines',
            name='Check contract deadlines',
            replace_existing=True
        )

    def start(self):
        """Запуск планировщика мониторинга"""
        try:
            self.scheduler.start()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")

    def stop(self):
        """Остановка планировщика"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")

    def update_tenders(self):
        """Обновление данных о тендерах из ЕИС"""
        try:
            # Получаем все активные тендеры
            active_tenders = Tender.query.filter(
                Tender.deadline > datetime.utcnow()
            ).all()

            for tender in active_tenders:
                # Парсим обновленные данные
                tender_data = self.parser.parse_tender(tender.tender_id)
                
                if tender_data:
                    # Обновляем данные в базе
                    tender.title = tender_data['title']
                    tender.description = tender_data['description']
                    tender.price = tender_data['price']
                    tender.customer = tender_data['customer']
                    tender.status = tender_data['status']
                    tender.updated_at = datetime.utcnow()

            db.session.commit()
            logger.info(f"Updated {len(active_tenders)} tenders")
            
        except Exception as e:
            logger.error(f"Error updating tenders: {str(e)}")
            db.session.rollback()

    def cleanup_old_tenders(self):
        """Очистка старых тендеров для оптимизации базы данных"""
        try:
            # Удаляем тендеры старше 30 дней
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            old_tenders = Tender.query.filter(
                Tender.deadline < cutoff_date
            ).all()

            for tender in old_tenders:
                db.session.delete(tender)

            db.session.commit()
            logger.info(f"Cleaned up {len(old_tenders)} old tenders")
            
        except Exception as e:
            logger.error(f"Error cleaning up old tenders: {str(e)}")
            db.session.rollback()
            
    def analyze_contract_anomalies(self):
        """
        Анализ аномалий в исполнении контрактов
        
        Использует ИИ-алгоритмы для выявления подозрительных паттернов
        в ценообразовании и поведении поставщиков
        """
        try:
            # Получаем активные контракты
            active_tenders = Tender.query.filter(
                Tender.status == 'active'
            ).all()
            
            anomalies_detected = 0
            
            for tender in active_tenders:
                # Подготовка данных для анализа
                tender_data = {
                    'title': tender.title,
                    'description': tender.description,
                    'price': tender.price,
                    'customer': tender.customer,
                    'deadline': tender.deadline if hasattr(tender, 'deadline') else datetime.utcnow()
                }
                
                # Анализ рисков с использованием ИИ
                risk_analysis = self.analyzer._analyze_risks(tender_data)
                
                # Если обнаружены аномалии, сохраняем результат
                if "высокий риск" in risk_analysis.lower() or "аномалия" in risk_analysis.lower():
                    # Здесь можно добавить логику сохранения аномалий
                    anomalies_detected += 1
            
            logger.info(f"Analyzed {len(active_tenders)} contracts, detected {anomalies_detected} anomalies")
            
        except Exception as e:
            logger.error(f"Error analyzing contract anomalies: {str(e)}")
    
    def check_contract_deadlines(self):
        """
        Проверка сроков исполнения контрактов
        
        Отслеживает соблюдение временных рамок исполнения контрактов
        и генерирует предупреждения о потенциальных нарушениях графика
        """
        try:
            # Получаем контракты с приближающимися сроками
            warning_date = datetime.utcnow() + timedelta(days=7)
            
            upcoming_deadlines = Tender.query.filter(
                Tender.deadline <= warning_date,
                Tender.deadline > datetime.utcnow(),
                Tender.status == 'active'
            ).all()
            
            for tender in upcoming_deadlines:
                days_left = (tender.deadline - datetime.utcnow()).days
                logger.info(f"Contract deadline warning: {tender.title} ({days_left} days left)")
                # Здесь можно добавить логику для отправки уведомлений
            
            logger.info(f"Checked deadlines: {len(upcoming_deadlines)} contracts approaching deadline")
            
        except Exception as e:
            logger.error(f"Error checking contract deadlines: {str(e)}")

def setup_scheduler(app):
    """
    Настройка и запуск планировщика задач для приложения
    """
    scheduler = TenderScheduler()
    
    # Запуск планировщика при старте приложения
    scheduler.start()
    
    # Регистрация функции остановки планировщика при завершении работы приложения
    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        scheduler.stop()
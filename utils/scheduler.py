from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging
from models import Tender, db
from .parser import TenderParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenderScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.parser = TenderParser()
        self.setup_jobs()

    def setup_jobs(self):
        """Настройка периодических задач"""
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

    def start(self):
        """Запуск планировщика"""
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
        """Обновление данных о тендерах"""
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
        """Очистка старых тендеров"""
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
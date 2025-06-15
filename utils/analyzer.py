import g4f
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenderAnalyzer:
    def __init__(self):
        self.model = "gpt-3.5-turbo"

    def analyze_tender(self, tender_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Полный анализ тендера с использованием g4f
        """
        try:
            return {
                'technical_analysis': self._analyze_technical(tender_data),
                'budget_analysis': self._analyze_budget(tender_data),
                'risk_analysis': self._analyze_risks(tender_data),
                'recommendations': self._generate_recommendations(tender_data)
            }
        except Exception as e:
            logger.error(f"Error analyzing tender: {str(e)}")
            return {
                'technical_analysis': "Ошибка анализа",
                'budget_analysis': "Ошибка анализа",
                'risk_analysis': "Ошибка анализа",
                'recommendations': "Ошибка анализа"
            }

    def _analyze_technical(self, tender_data: Dict[str, Any]) -> str:
        """Анализ технического задания"""
        prompt = f"""
        Проанализируй техническое задание тендера:
        Название: {tender_data['title']}
        Описание: {tender_data['description']}
        
        Оцени:
        1. Сложность выполнения
        2. Ключевые требования
        3. Потенциальные сложности
        4. Необходимые компетенции
        """
        
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response

    def _analyze_budget(self, tender_data: Dict[str, Any]) -> str:
        """Анализ бюджета тендера"""
        prompt = f"""
        Проанализируй бюджет тендера:
        Название: {tender_data['title']}
        Цена: {tender_data['price']}
        
        Оцени:
        1. Адекватность бюджета
        2. Потенциальную рентабельность
        3. Сравнение с рыночными ценами
        4. Рекомендации по ценообразованию
        """
        
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response

    def _analyze_risks(self, tender_data: Dict[str, Any]) -> str:
        """Анализ рисков участия в тендере"""
        prompt = f"""
        Проанализируй риски участия в тендере:
        Название: {tender_data['title']}
        Заказчик: {tender_data['customer']}
        Срок подачи: {tender_data['deadline']}
        
        Оцени:
        1. Основные риски
        2. Вероятность успеха
        3. Потенциальные проблемы
        4. Меры по снижению рисков
        """
        
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response

    def _generate_recommendations(self, tender_data: Dict[str, Any]) -> str:
        """Генерация рекомендаций по участию в тендере"""
        prompt = f"""
        Сформулируй рекомендации по участию в тендере:
        Название: {tender_data['title']}
        Заказчик: {tender_data['customer']}
        Цена: {tender_data['price']}
        
        Предоставь:
        1. Общую рекомендацию по участию
        2. Ключевые моменты для подготовки
        3. Стратегию участия
        4. Потенциальные преимущества
        """
        
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response 
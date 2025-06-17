import g4f
import logging
from typing import Dict, Any, List, Tuple
import re
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenderAnalyzer:
    """
    Анализатор тендеров с использованием ИИ
    
    Использует передовые технологии искусственного интеллекта для обеспечения
    соответствия исполнения контрактов требованиям законодательства и повышения
    качества государственного управления.
    """
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.confidential_mode = False

    def set_confidential_mode(self, enabled: bool = True):
        """
        Включение/выключение режима конфиденциального анализа
        
        В режиме конфиденциального анализа данные пользователей не сохраняются
        после завершения сессии, что обеспечивает максимальную защиту
        коммерческой информации.
        """
        self.confidential_mode = enabled
        logger.info(f"Confidential mode {'enabled' if enabled else 'disabled'}")

    def analyze_tender(self, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Полный анализ тендера с использованием ИИ
        
        Проводит комплексный анализ тендера по различным аспектам:
        - Техническое задание
        - Бюджет и ценообразование
        - Риски исполнения
        - Соответствие требованиям законодательства
        - Рекомендации
        """
        try:
            # Базовый анализ
            analysis_results = {
                'technical_analysis': self._analyze_technical(tender_data),
                'budget_analysis': self._analyze_budget(tender_data),
                'risk_analysis': self._analyze_risks(tender_data),
                'compliance_analysis': self._analyze_compliance(tender_data),
                'recommendations': self._generate_recommendations(tender_data)
            }
            
            # Расчет оценки риска
            risk_score = self._calculate_risk_score(analysis_results)
            analysis_results['risk_score'] = risk_score
            
            # Выявление аномалий
            anomalies = self._detect_anomalies(tender_data, analysis_results)
            analysis_results['anomalies'] = anomalies
            
            # Очистка данных в конфиденциальном режиме
            if self.confidential_mode:
                analysis_results = self._sanitize_confidential_data(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing tender: {str(e)}")
            return {
                'technical_analysis': "Ошибка анализа",
                'budget_analysis': "Ошибка анализа",
                'risk_analysis': "Ошибка анализа",
                'compliance_analysis': "Ошибка анализа",
                'recommendations': "Ошибка анализа",
                'risk_score': 0.0,
                'anomalies': []
            }

    def _analyze_technical(self, tender_data: Dict[str, Any]) -> str:
        """
        Анализ технического задания
        
        Оценивает сложность, требования и потенциальные проблемы
        в техническом задании контракта.
        """
        prompt = f"""
        Проанализируй техническое задание государственного контракта:
        Название: {tender_data['title']}
        Описание: {tender_data['description']}
        Заказчик: {tender_data.get('customer', 'Не указан')}
        
        Оцени следующие аспекты:
        1. Сложность выполнения технического задания
        2. Ключевые требования и их обоснованность
        3. Потенциальные сложности и узкие места в реализации
        4. Необходимые компетенции для исполнения
        5. Соответствие техзадания целям закупки
        6. Возможные риски неисполнения из-за технических требований
        
        Предоставь структурированный анализ с конкретными выводами по каждому пункту.
        """
        
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response

    def _analyze_budget(self, tender_data: Dict[str, Any]) -> str:
        """
        Анализ бюджета и ценообразования
        
        Выявляет аномалии в ценообразовании и оценивает
        адекватность бюджета контракта.
        """
        initial_price = tender_data.get('initial_price', tender_data.get('price', 0))
        final_price = tender_data.get('price', initial_price)
        
        prompt = f"""
        Проанализируй бюджет государственного контракта:
        Название: {tender_data['title']}
        Начальная цена: {initial_price} руб.
        Итоговая цена: {final_price} руб.
        
        Оцени следующие аспекты:
        1. Адекватность бюджета относительно объема работ
        2. Наличие признаков завышения или занижения цены
        3. Сравнение с рыночными ценами на аналогичные услуги/товары
        4. Обоснованность ценообразования
        5. Потенциальные риски перерасхода бюджета
        6. Возможные признаки коррупционных схем в ценообразовании
        
        Предоставь детальный анализ с количественными оценками и конкретными выводами.
        """
        
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response

    def _analyze_risks(self, tender_data: Dict[str, Any]) -> str:
        """
        Анализ рисков исполнения контракта
        
        Выявляет потенциальные риски неисполнения или
        некачественного исполнения контракта.
        """
        deadline = tender_data.get('execution_deadline', tender_data.get('deadline', 'Не указан'))
        if isinstance(deadline, datetime):
            deadline = deadline.strftime('%d.%m.%Y')
            
        prompt = f"""
        Проанализируй риски исполнения государственного контракта:
        Название: {tender_data['title']}
        Заказчик: {tender_data.get('customer', 'Не указан')}
        Поставщик: {tender_data.get('supplier', 'Не определен')}
        Срок исполнения: {deadline}
        Цена: {tender_data.get('price', 'Не указана')} руб.
        
        Оцени следующие риски:
        1. Риски срыва сроков исполнения
        2. Риски некачественного исполнения
        3. Риски изменения условий контракта
        4. Финансовые риски для бюджета
        5. Репутационные риски для заказчика
        6. Риски нарушения законодательства о закупках
        7. Риски недобросовестного поведения поставщика
        
        Для каждого риска укажи:
        - Вероятность (низкая/средняя/высокая)
        - Потенциальный ущерб (низкий/средний/высокий)
        - Рекомендуемые меры по снижению риска
        """
        
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response

    def _analyze_compliance(self, tender_data: Dict[str, Any]) -> str:
        """
        Анализ соответствия требованиям законодательства
        
        Проверяет соответствие контракта требованиям ФЗ-44, ФЗ-223
        и других нормативных актов.
        """
        prompt = f"""
        Проанализируй соответствие государственного контракта требованиям законодательства РФ:
        Название: {tender_data['title']}
        Заказчик: {tender_data.get('customer', 'Не указан')}
        Цена: {tender_data.get('price', 'Не указана')} руб.
        
        Оцени соответствие следующим требованиям:
        1. Федеральный закон №44-ФЗ "О контрактной системе"
        2. Федеральный закон №223-ФЗ (если применимо)
        3. Постановления Правительства РФ о государственных закупках
        4. Требования к обоснованию НМЦК
        5. Требования к описанию объекта закупки
        6. Требования к срокам проведения процедур
        7. Требования к обеспечению исполнения контракта
        
        Укажи конкретные статьи законов и нормативных актов, которым должен соответствовать контракт.
        Выяви потенциальные несоответствия и нарушения законодательства.
        """
        
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response

    def _generate_recommendations(self, tender_data: Dict[str, Any]) -> str:
        """
        Генерация рекомендаций по контролю исполнения контракта
        
        Формирует рекомендации по мониторингу и контролю
        качества исполнения контракта.
        """
        prompt = f"""
        Сформулируй рекомендации по контролю исполнения государственного контракта:
        Название: {tender_data['title']}
        Заказчик: {tender_data.get('customer', 'Не указан')}
        Цена: {tender_data.get('price', 'Не указана')} руб.
        
        Предоставь конкретные рекомендации по следующим аспектам:
        1. Ключевые контрольные точки для мониторинга исполнения
        2. Методы проверки качества поставляемых товаров/услуг
        3. Документы, которые необходимо проверять в процессе исполнения
        4. Действия при выявлении отклонений от условий контракта
        5. Меры по предотвращению коррупционных рисков
        6. Рекомендации по взаимодействию с поставщиком
        7. Порядок приемки результатов исполнения контракта
        
        Рекомендации должны быть конкретными, практическими и применимыми.
        """
        
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response
        
    def _calculate_risk_score(self, analysis_results: Dict[str, str]) -> float:
        """
        Расчет интегральной оценки риска контракта
        
        Анализирует результаты всех видов анализа и вычисляет
        общую оценку риска по шкале от 0 до 100.
        """
        try:
            # Анализ ключевых слов риска в результатах анализа
            risk_keywords = [
                "высокий риск", "серьезные нарушения", "критические проблемы",
                "несоответствие требованиям", "завышение цены", "коррупционные риски",
                "недобросовестный поставщик", "срыв сроков", "некачественное исполнение"
            ]
            
            warning_keywords = [
                "средний риск", "потенциальные проблемы", "требует внимания",
                "возможные нарушения", "неоптимальная цена", "сомнительные условия"
            ]
            
            # Подсчет упоминаний рисков
            risk_count = 0
            warning_count = 0
            
            for analysis_text in analysis_results.values():
                if isinstance(analysis_text, str):
                    for keyword in risk_keywords:
                        risk_count += analysis_text.lower().count(keyword.lower())
                    
                    for keyword in warning_keywords:
                        warning_count += analysis_text.lower().count(keyword.lower())
            
            # Расчет базовой оценки риска
            base_score = min(100, (risk_count * 10 + warning_count * 5))
            
            # Анализ бюджета на предмет аномалий
            budget_analysis = analysis_results.get('budget_analysis', '')
            if isinstance(budget_analysis, str):
                if "завышение цены" in budget_analysis.lower():
                    base_score += 15
                if "необоснованное ценообразование" in budget_analysis.lower():
                    base_score += 10
            
            # Анализ соответствия требованиям
            compliance_analysis = analysis_results.get('compliance_analysis', '')
            if isinstance(compliance_analysis, str):
                if "нарушение закона" in compliance_analysis.lower():
                    base_score += 20
                if "несоответствие требованиям" in compliance_analysis.lower():
                    base_score += 15
            
            # Нормализация оценки
            final_score = min(100, max(0, base_score))
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return 50.0  # Средний риск по умолчанию
    
    def _detect_anomalies(self, tender_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Выявление аномалий в контракте
        
        Анализирует данные контракта и результаты анализа для выявления
        подозрительных паттернов и аномалий.
        """
        anomalies = []
        
        try:
            # Проверка аномалий в цене
            initial_price = tender_data.get('initial_price', 0)
            final_price = tender_data.get('price', 0)
            
            if initial_price and final_price:
                # Аномально низкое снижение цены (менее 0.5%)
                if 0 < (initial_price - final_price) / initial_price < 0.005:
                    anomalies.append({
                        'anomaly_type': 'price_reduction',
                        'description': 'Аномально низкое снижение цены контракта',
                        'severity': 'medium'
                    })
                
                # Аномально высокое снижение цены (более 40%)
                if (initial_price - final_price) / initial_price > 0.4:
                    anomalies.append({
                        'anomaly_type': 'dumping',
                        'description': 'Возможный демпинг цены, риск некачественного исполнения',
                        'severity': 'high'
                    })
            
            # Проверка сроков исполнения
            if 'execution_deadline' in tender_data and 'publication_date' in tender_data:
                execution_deadline = tender_data['execution_deadline']
                publication_date = tender_data['publication_date']
                
                if isinstance(execution_deadline, datetime) and isinstance(publication_date, datetime):
                    days_for_execution = (execution_deadline - publication_date).days
                    
                    # Аномально короткий срок исполнения
                    if days_for_execution < 10:
                        anomalies.append({
                            'anomaly_type': 'short_deadline',
                            'description': 'Аномально короткий срок исполнения контракта',
                            'severity': 'high'
                        })
            
            # Анализ текстовых результатов на предмет аномалий
            risk_analysis = analysis_results.get('risk_analysis', '')
            budget_analysis = analysis_results.get('budget_analysis', '')
            
            # Поиск признаков коррупции
            corruption_patterns = [
                r'коррупц\w+', r'откат\w*', r'аффилирован\w+', 
                r'конфликт\s+интересов', r'сговор\w*'
            ]
            
            for pattern in corruption_patterns:
                for analysis_text in [risk_analysis, budget_analysis]:
                    if re.search(pattern, analysis_text, re.IGNORECASE):
                        anomalies.append({
                            'anomaly_type': 'corruption_risk',
                            'description': 'Выявлены признаки потенциальных коррупционных рисков',
                            'severity': 'critical'
                        })
                        break
                else:
                    continue
                break
            
            # Оценка риска на основе интегрального показателя
            risk_score = analysis_results.get('risk_score', 0)
            if risk_score > 75:
                anomalies.append({
                    'anomaly_type': 'high_risk_score',
                    'description': f'Высокий интегральный показатель риска: {risk_score}',
                    'severity': 'high'
                })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return []
    
    def _sanitize_confidential_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Очистка конфиденциальных данных
        
        В режиме конфиденциального анализа удаляет или маскирует
        чувствительную информацию из результатов анализа.
        """
        if not self.confidential_mode:
            return analysis_results
            
        sanitized_results = {}
        
        # Маскирование персональных данных и коммерческой информации
        for key, value in analysis_results.items():
            if isinstance(value, str):
                # Маскирование ИНН
                value = re.sub(r'\b\d{10,12}\b', '[ИНН]', value)
                
                # Маскирование email
                value = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', value)
                
                # Маскирование телефонов
                value = re.sub(r'\b(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}\b', '[ТЕЛЕФОН]', value)
                
                sanitized_results[key] = value
            else:
                sanitized_results[key] = value
                
        # Добавление метки о конфиденциальном режиме
        sanitized_results['confidential_mode'] = True
        
        return sanitized_results
        
    def analyze_contract_execution(self, contract_data: Dict[str, Any], milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Анализ хода исполнения контракта
        
        Оценивает соблюдение сроков, качество исполнения и соответствие
        результатов требованиям контракта.
        """
        try:
            # Подготовка данных о контракте и этапах
            milestones_info = "\n".join([
                f"Этап: {m.get('title', 'Без названия')}, "
                f"Срок: {m.get('due_date', 'Не указан')}, "
                f"Статус: {m.get('status', 'Не указан')}"
                for m in milestones
            ])
            
            prompt = f"""
            Проанализируй ход исполнения государственного контракта:
            Название: {contract_data.get('title', 'Не указано')}
            Заказчик: {contract_data.get('customer', 'Не указан')}
            Поставщик: {contract_data.get('supplier', 'Не указан')}
            Цена: {contract_data.get('price', 'Не указана')} руб.
            Срок исполнения: {contract_data.get('execution_deadline', 'Не указан')}
            
            Этапы исполнения:
            {milestones_info}
            
            Проведи анализ по следующим аспектам:
            1. Соблюдение сроков исполнения контракта
            2. Качество исполнения промежуточных этапов
            3. Риски срыва итоговых сроков
            4. Соответствие промежуточных результатов требованиям контракта
            5. Рекомендации по дальнейшему контролю исполнения
            
            Предоставь детальный анализ с конкретными выводами и рекомендациями.
            """
            
            response = g4f.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Расчет процента выполнения
            completed_milestones = sum(1 for m in milestones if m.get('status') == 'completed')
            completion_percentage = (completed_milestones / len(milestones)) * 100 if milestones else 0
            
            # Оценка соблюдения сроков
            overdue_milestones = sum(1 for m in milestones 
                                    if m.get('status') != 'completed' and 
                                    m.get('due_date') and 
                                    isinstance(m['due_date'], datetime) and 
                                    m['due_date'] < datetime.now())
            
            schedule_status = "В срок"
            if overdue_milestones > 0:
                schedule_status = f"Отставание от графика ({overdue_milestones} этапов)"
            
            return {
                'execution_analysis': response,
                'completion_percentage': completion_percentage,
                'schedule_status': schedule_status,
                'overdue_milestones': overdue_milestones,
                'total_milestones': len(milestones)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing contract execution: {str(e)}")
            return {
                'execution_analysis': "Ошибка анализа исполнения контракта",
                'completion_percentage': 0,
                'schedule_status': "Ошибка анализа",
                'overdue_milestones': 0,
                'total_milestones': len(milestones) if milestones else 0
            }
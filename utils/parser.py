import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenderParser:
    def __init__(self):
        self.base_url = "https://zakupki.gov.ru"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def parse_tender(self, tender_id):
        """
        Парсинг информации о конкретном тендере
        """
        try:
            url = f"{self.base_url}/epz/order/extendedsearch/results.html?searchString={tender_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлечение основной информации о тендере
            tender_data = {
                'tender_id': tender_id,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'price': self._extract_price(soup),
                'customer': self._extract_customer(soup),
                'publication_date': self._extract_publication_date(soup),
                'deadline': self._extract_deadline(soup),
                'status': self._extract_status(soup)
            }
            
            return tender_data
            
        except Exception as e:
            logger.error(f"Error parsing tender {tender_id}: {str(e)}")
            return None

    def _extract_title(self, soup):
        """Извлечение заголовка тендера"""
        title_elem = soup.find('div', {'class': 'registry-entry__header-mid-title'})
        return title_elem.text.strip() if title_elem else ""

    def _extract_description(self, soup):
        """Извлечение описания тендера"""
        desc_elem = soup.find('div', {'class': 'registry-entry__body-value'})
        return desc_elem.text.strip() if desc_elem else ""

    def _extract_price(self, soup):
        """Извлечение цены тендера"""
        price_elem = soup.find('div', {'class': 'price-block__value'})
        if price_elem:
            try:
                return float(price_elem.text.strip().replace(' ', '').replace(',', '.'))
            except ValueError:
                return None
        return None

    def _extract_customer(self, soup):
        """Извлечение информации о заказчике"""
        customer_elem = soup.find('div', {'class': 'registry-entry__body-href'})
        return customer_elem.text.strip() if customer_elem else ""

    def _extract_publication_date(self, soup):
        """Извлечение даты публикации"""
        date_elem = soup.find('div', {'class': 'data-block__value'})
        if date_elem:
            try:
                return datetime.strptime(date_elem.text.strip(), '%d.%m.%Y')
            except ValueError:
                return None
        return None

    def _extract_deadline(self, soup):
        """Извлечение срока подачи заявок"""
        deadline_elem = soup.find('div', {'class': 'data-block__value'})
        if deadline_elem:
            try:
                return datetime.strptime(deadline_elem.text.strip(), '%d.%m.%Y')
            except ValueError:
                return None
        return None

    def _extract_status(self, soup):
        """Извлечение статуса тендера"""
        status_elem = soup.find('div', {'class': 'registry-entry__header-mid__title'})
        return status_elem.text.strip() if status_elem else "" 
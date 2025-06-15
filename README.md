# OpenTender MVP

OpenTender MVP - это минимально жизнеспособный продукт для автоматизированного анализа государственных закупок России. Проект использует современный технологический стек для быстрого вывода на рынок при минимальных затратах на разработку.

## Технологический стек

### Backend
- Python 3.11+
- Flask 3.0+
- SQLite 3.40+
- g4f (GPT-4 Free)
- BeautifulSoup4
- APScheduler

### Frontend
- React 18.3+
- Tailwind CSS 4.0+
- Axios
- Chart.js 4.x

## Установка и запуск

### Требования
- Python 3.11 или выше
- Node.js 18 или выше
- npm или yarn

### Backend

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл .env в корневой директории:
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///opentender.db
LOG_LEVEL=INFO
```

4. Запустите сервер:
```bash
python app.py
```

### Frontend

1. Перейдите в директорию frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
# или
yarn install
```

3. Запустите сервер разработки:
```bash
npm start
# или
yarn start
```

## Основные функции

- Автоматический парсинг данных с сайта госзакупок
- Анализ технических заданий с помощью ИИ
- Оценка бюджета и рисков
- Генерация рекомендаций по участию
- Планировщик обновления данных
- REST API для интеграции

## API Endpoints

### Аутентификация
- POST /api/auth/register - Регистрация нового пользователя
- POST /api/auth/login - Вход в систему

### Тендеры
- GET /api/tenders - Получение списка тендеров
- POST /api/tenders/{id}/analyze - Анализ конкретного тендера

### Профиль
- GET /api/profile - Получение информации о пользователе

## Безопасность

- JWT-аутентификация
- Rate limiting
- CORS защита
- Шифрование чувствительных данных

## Лицензия

MIT License

## Контакты

Для вопросов и предложений обращайтесь: [ваш email] 
from flask import Flask, request, jsonify
import os
from config import Config
from extensions import init_extensions, db
from datetime import timedelta
from werkzeug.utils import secure_filename

def create_app(config_name='default'):
    """
    Создание и настройка экземпляра приложения Flask
    
    OpenTender - инновационная ИИ-платформа для автоматизированного контроля 
    исполнения государственных контрактов в РФ, построенная на принципах 
    цифровой прозрачности и эффективного мониторинга бюджетных расходов.
    
    Args:
        config_name: Имя конфигурации ('development', 'testing', 'production')
    """
    app = Flask(__name__)

    # Загрузка конфигурации
    app.config.from_object(Config)
    
    # Настройка базовых параметров
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///opentender.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    
    # Настройка загрузки файлов
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    # OAuth конфигурация для российских и международных платформ
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
    
    # Настройка безопасности
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    
    # Настройка CORS
    app.config['CORS_ORIGINS'] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://opentender.ru"
    ]

    # Инициализация всех расширений
    init_extensions(app)
    
    # Регистрация маршрутов
    from routes import register_routes
    register_routes(app)
    
    # Регистрация модулей мониторинга и анализа
    register_monitoring_modules(app)
    
    # Создание директорий для загрузки файлов
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'temp'), exist_ok=True)
    
    # Регистрация API для чата с ИИ
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        """API для обработки запросов к ИИ с поддержкой файлов"""
        try:
            # Проверяем, пришли ли данные как JSON или как форма
            if request.is_json:
                # Обработка JSON запроса
                data = request.get_json()
                if not data or not data.get('message'):
                    return jsonify({'error': 'Сообщение не предоставлено'}), 400
                
                message = data.get('message')
                model = data.get('model', 'gemini-1.5-flash')
                category = data.get('category', 'text')
                full_message = message
                files = []
            else:
                # Обработка формы с файлами
                message = request.form.get('message', '')
                model = request.form.get('model', 'gemini-1.5-flash')
                category = request.form.get('category', 'text')
                
                # Обрабатываем загруженные файлы
                files = []
                file_contents = []
                
                for key in request.files:
                    file = request.files[key]
                    if file.filename:
                        # Создаем временную директорию для файлов, если она не существует
                        upload_dir = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'temp')
                        os.makedirs(upload_dir, exist_ok=True)
                        
                        # Сохраняем файл
                        filename = os.path.join(upload_dir, secure_filename(file.filename))
                        file.save(filename)
                        files.append(filename)
                        
                        # Если это текстовый файл, читаем его содержимое
                        if file.content_type.startswith('text/') or file.filename.endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json')):
                            try:
                                with open(filename, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    file_contents.append(f"Содержимое файла {file.filename}:\n\n{content}")
                            except UnicodeDecodeError:
                                file_contents.append(f"Файл {file.filename} не может быть прочитан как текст.")
                
                # Добавляем содержимое файлов к сообщению
                if file_contents:
                    full_message = f"{message}\n\n" + "\n\n".join(file_contents)
                else:
                    full_message = message
            
            # Импортируем g4f
            import g4f
            
            # Определяем провайдера и модель на основе выбранной категории и модели
            provider = None
            model_name = model
            
            # Маппинг категорий и моделей на провайдеров g4f
            providers_map = {
                'text': {
                    'gemini-1.5-flash': (g4f.Provider.TeachAnything, 'gemini-1.5-flash'),
                    'gemini-1.5-pro': (g4f.Provider.TeachAnything, 'gemini-1.5-pro'),
                    'command-r': (g4f.Provider.CohereForAI_C4AI_Command, 'command-r'),
                    'command-r-plus': (g4f.Provider.CohereForAI_C4AI_Command, 'command-r-plus'),
                    'qwen-3-30b': (g4f.Provider.Qwen_Qwen_3, 'qwen-3-30b-a3b'),
                    'claude-3-opus': (g4f.Provider.Anthropic, 'claude-3-opus'),
                    'claude-3-sonnet': (g4f.Provider.Anthropic, 'claude-3-sonnet'),
                    'claude-3-haiku': (g4f.Provider.Anthropic, 'claude-3-haiku'),
                    'llama-3-70b': (g4f.Provider.Groq, 'llama-3-70b-8192'),
                    'llama-3-8b': (g4f.Provider.Groq, 'llama-3-8b-8192')
                },
                'code': {
                    'gpt-4': (g4f.Provider.Yqcloud, 'gpt-4'),
                    'gpt-4-turbo': (g4f.Provider.Yqcloud, 'gpt-4-turbo'),
                    'gpt-3.5-turbo': (g4f.Provider.Yqcloud, 'gpt-3.5-turbo'),
                    'blackbox-python': (g4f.Provider.Blackbox, 'Python Agent'),
                    'blackbox-js': (g4f.Provider.Blackbox, 'JavaScript Agent'),
                    'blackbox-react': (g4f.Provider.Blackbox, 'React Agent'),
                    'blackbox-sql': (g4f.Provider.Blackbox, 'SQL Agent'),
                    'blackbox-java': (g4f.Provider.Blackbox, 'Java Agent'),
                    'claude-3-opus-code': (g4f.Provider.Anthropic, 'claude-3-opus'),
                    'codellama-70b': (g4f.Provider.Groq, 'codellama-70b')
                },
                'research': {
                    'perplexity-r1-1776': (g4f.Provider.PerplexityLabs, 'r1-1776'),
                    'perplexity-sonar-small': (g4f.Provider.PerplexityLabs, 'sonar-small-online'),
                    'perplexity-sonar-medium': (g4f.Provider.PerplexityLabs, 'sonar-medium-online'),
                    'deepseek-r1': (g4f.Provider.LambdaChat, 'deepseek-r1'),
                    'sonar-reasoning-pro': (g4f.Provider.PerplexityLabs, 'sonar-reasoning-pro'),
                    'hermes-3-llama-405b': (g4f.Provider.LambdaChat, 'hermes-3-llama-3.1-405b-fp8'),
                    'mixtral-8x7b': (g4f.Provider.Groq, 'mixtral-8x7b-32768'),
                    'claude-3-opus-research': (g4f.Provider.Anthropic, 'claude-3-opus'),
                    'gemini-1.5-pro-research': (g4f.Provider.TeachAnything, 'gemini-1.5-pro'),
                    'gpt-4-research': (g4f.Provider.Yqcloud, 'gpt-4')
                },
                'multimodal': {
                    'gemini-1.5-pro': (g4f.Provider.TeachAnything, 'gemini-1.5-pro'),
                    'gemini-1.5-flash': (g4f.Provider.TeachAnything, 'gemini-1.5-flash'),
                    'claude-3-opus-vision': (g4f.Provider.Anthropic, 'claude-3-opus'),
                    'claude-3-sonnet-vision': (g4f.Provider.Anthropic, 'claude-3-sonnet'),
                    'gpt-4-vision': (g4f.Provider.Yqcloud, 'gpt-4-vision'),
                    'llava-1.6': (g4f.Provider.LambdaChat, 'llava-1.6-34b'),
                    'cogvlm-17b': (g4f.Provider.LambdaChat, 'cogvlm-17b'),
                    'qwen-vl': (g4f.Provider.Qwen_Qwen_3, 'qwen-vl'),
                    'fuyu-8b': (g4f.Provider.LambdaChat, 'fuyu-8b'),
                    'bakllava-1': (g4f.Provider.LambdaChat, 'bakllava-1')
                }
            }
            
            # Получаем провайдера и модель из маппинга
            if category in providers_map and model in providers_map[category]:
                provider, model_name = providers_map[category][model]
            else:
                # Провайдер и модель по умолчанию
                provider = g4f.Provider.TeachAnything
                model_name = 'gemini-1.5-flash'
            
            app.logger.info(f"Using provider: {provider.__name__}, model: {model_name}")
            
            # Получаем ответ от модели
            response = g4f.ChatCompletion.create(
                model=model_name,
                provider=provider,
                messages=[{"role": "user", "content": full_message}]
            )
            
            # Удаляем временные файлы
            for file_path in files:
                try:
                    os.remove(file_path)
                except Exception as e:
                    app.logger.error(f"Error removing temporary file {file_path}: {str(e)}")
            
            return jsonify({
                'response': response,
                'model': model_name,
                'provider': provider.__name__ if provider else None
            })
            
        except Exception as e:
            app.logger.error(f"Error in chat API: {str(e)}")
            return jsonify({
                'error': 'Произошла ошибка при обработке запроса',
                'details': str(e)
            }), 500

    return app

def register_monitoring_modules(app):
    """
    Регистрация модулей мониторинга и анализа контрактов
    
    Инициализирует компоненты для анализа тендеров, парсинга данных
    и автоматического мониторинга исполнения контрактов.
    """
    from utils.analyzer import TenderAnalyzer
    from utils.parser import TenderParser
    
    app.tender_analyzer = TenderAnalyzer()
    app.tender_parser = TenderParser()
    
    # Инициализация планировщика задач для автоматического мониторинга
    if not app.debug:
        from utils.scheduler import setup_scheduler
        setup_scheduler(app)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
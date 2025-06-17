def register_chat_api(app):
    """
    Регистрирует API маршрут для чата с ИИ
    """
    from flask import request, jsonify
    import os
    
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
                        filename = os.path.join(upload_dir, file.filename)
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
                    'qwen-3-30b': (g4f.Provider.Qwen_Qwen_3, 'qwen-3-30b-a3b')
                },
                'code': {
                    'gpt-4': (g4f.Provider.Yqcloud, 'gpt-4'),
                    'blackbox-python': (g4f.Provider.Blackbox, 'Python Agent'),
                    'blackbox-js': (g4f.Provider.Blackbox, 'JavaScript Agent'),
                    'blackbox-react': (g4f.Provider.Blackbox, 'React Agent')
                },
                'research': {
                    'perplexity-r1-1776': (g4f.Provider.PerplexityLabs, 'r1-1776'),
                    'deepseek-r1': (g4f.Provider.LambdaChat, 'deepseek-r1'),
                    'sonar-reasoning-pro': (g4f.Provider.PerplexityLabs, 'sonar-reasoning-pro'),
                    'hermes-3-llama-405b': (g4f.Provider.LambdaChat, 'hermes-3-llama-3.1-405b-fp8')
                },
                'multimodal': {
                    'gemini-1.5-pro': (g4f.Provider.TeachAnything, 'gemini-1.5-pro'),
                    'gemini-1.5-flash': (g4f.Provider.TeachAnything, 'gemini-1.5-flash')
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
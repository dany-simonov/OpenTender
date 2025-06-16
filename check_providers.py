import g4f
import asyncio
from typing import List, Dict
import json
from datetime import datetime
import inspect

async def test_provider_with_model(provider_name: str, model: str) -> Dict:
    """Тестирует конкретную модель провайдера"""
    try:
        provider_class = getattr(g4f.Provider, provider_name)
        if not inspect.isclass(provider_class):
            return None
            
        provider = provider_class()
        response = await g4f.ChatCompletion.create_async(
            model=model,
            provider=provider,
            messages=[{"role": "user", "content": "Привет, как дела?"}]
        )
        
        return {
            "provider": provider_name,
            "model": model,
            "response": response
        }
    except Exception as e:
        return None

async def test_all_providers() -> List[Dict]:
    """Тестирует все провайдеры и их модели"""
    successful_results = []
    all_providers = set()
    sub_providers = set()
    
    providers = [name for name in dir(g4f.Provider) if not name.startswith('_')]
    
    for provider_name in providers:
        try:
            provider_class = getattr(g4f.Provider, provider_name)
            if not inspect.isclass(provider_class):
                continue
                
            provider = provider_class()
            all_providers.add(provider_name)
            
            # Получаем список моделей для провайдера
            if hasattr(provider, 'models'):
                models = provider.models
            else:
                # Если нет явного списка моделей, пробуем стандартные
                models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']
            
            print(f"\nТестируем провайдер: {provider_name}")
            print(f"Доступные модели: {models}")
            
            for model in models:
                print(f"Тестируем модель: {model}")
                result = await test_provider_with_model(provider_name, model)
                
                if result:
                    successful_results.append(result)
                    sub_providers.add(f"{provider_name} ({model})")
                    print(f"✅ {provider_name} ({model}): Успешно")
                    print(f"Ответ: {result['response']}")
                else:
                    print(f"❌ {provider_name} ({model}): Не удалось подключиться")
                    
        except Exception as e:
            print(f"❌ {provider_name}: Ошибка при инициализации")
            print(f"Ошибка: {str(e)}")
    
    return successful_results, all_providers, sub_providers

async def main():
    results, all_providers, sub_providers = await test_all_providers()
    
    # Сохраняем только успешные результаты в JSON файл
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"successful_providers_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Выводим подробную статистику
    print("\n" + "="*50)
    print("СТАТИСТИКА ТЕСТИРОВАНИЯ")
    print("="*50)
    print(f"\nВсего провайдеров: {len(all_providers)}")
    print(f"Всего под-провайдеров (провайдер + модель): {len(sub_providers)}")
    print(f"Успешно работающих под-провайдеров: {len(results)}")
    
    print("\nСписок успешно работающих под-провайдеров:")
    for result in results:
        print(f"✅ {result['provider']} ({result['model']})")
    
    print(f"\nРезультаты сохранены в файл: {filename}")

if __name__ == "__main__":
    asyncio.run(main()) 
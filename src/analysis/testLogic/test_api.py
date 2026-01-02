"""
Простой тест API (запускать после старта сервера).
"""

import requests

API_URL = "http://localhost:8000"


def test_health():
    """Проверка работоспособности."""
    print("\n[TEST] Health check")
    response = requests.get(f"{API_URL}/health")
    
    if response.status_code == 200:
        print(f"  ✓ Сервис работает: {response.json()}")
        return True
    else:
        print(f"  ✗ Ошибка: {response.status_code}")
        return False


def test_list_uploads():
    """Тест получения списка папок в uploads."""
    print("\n[TEST] List uploads")
    response = requests.get(f"{API_URL}/api/uploads")
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✓ Найдено папок: {result['count']}")
        if result['folders']:
            print(f"  Папки: {result['folders']}")
        return True
    else:
        print(f"  ✗ Ошибка: {response.status_code}")
        return False


def test_analyze():
    """Тест анализа данных из папки uploads."""
    print("\n[TEST] Analyze uploads")
    
    # Используем тестовую папку (предполагаем, что data/mock/01 скопирована в uploads)
    date_folder = "04"
    
    response = requests.get(f"{API_URL}/api/analyze/{date_folder}")
    
    if response.status_code == 200:
        result = response.json()
        print("  ✓ Анализ выполнен")
        print(f"  Обработано файлов: {len(result['files_processed'])}")
        
        # Проходные баллы
        if 'data' in result and 'passing_score' in result['data']:
            scores = result['data']['passing_score']
            print(f"  Проходные баллы:")
            for prog, score in scores.items():
                print(f"    {prog}: {score if score else 'НЕДОБОР'}")
        
        return True
    elif response.status_code == 404:
        print(f"  ⚠ Папка '{date_folder}' не найдена в uploads")
        print(f"  Подсказка: скопируйте data/mock/01 в data/uploads/01")
        return False
    else:
        print(f"  ✗ Ошибка: {response.status_code}")
        print(f"  {response.text}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ API")
    print("=" * 60)
    
    try:
        test_health()
        test_list_uploads()
        test_analyze()
        
        print("\n" + "=" * 60)
        print("ТЕСТЫ ЗАВЕРШЕНЫ")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Не удалось подключиться к API")
        print("  Запустите сервер: python3 api_manager.py")

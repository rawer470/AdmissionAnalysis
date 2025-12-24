"""
Тест класса AdmissionManager на данных из /data/mock
"""

import json
import os
from admission_stats import AdmissionManager


def load_mock_data():
    """Загрузить тестовые данные из data/mock."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    mock_dir = os.path.join(base_dir, 'data', 'mock')
    
    data = {}
    for prog in ['pm', 'ivt', 'itss', 'ib']:
        path = os.path.join(mock_dir, f'{prog}.json')
        with open(path, 'r', encoding='utf-8') as f:
            data[prog] = json.load(f)
    
    return data


def test_admission():
    """Основной тест распределения."""
    print("=" * 60)
    print("ТЕСТ AdmissionManager")
    print("=" * 60)
    
    # Загружаем данные
    data = load_mock_data()
    
    # Квоты (маленькие для наглядности)
    capacity = {
        'pm': 2,
        'ivt': 2,
        'itss': 1,
        'ib': 1
    }
    
    # Создаём менеджер
    manager = AdmissionManager(data, capacity)
    
    # --- Тест 1: Проходные баллы ---
    print("\n[TEST 1] calculate_passing_score()")
    scores = manager.calculate_passing_score()
    print(f"  Результат: {scores}")
    
    assert scores['pm'] is None, "ПМ должен быть в недоборе"
    assert scores['ivt'] == 240, f"ИВТ проходной должен быть 240, получили {scores['ivt']}"
    assert scores['itss'] == 260, f"ИТСС проходной должен быть 260, получили {scores['itss']}"
    assert scores['ib'] == 290, f"ИБ проходной должен быть 290, получили {scores['ib']}"
    print("  ✓ Проходные баллы корректны")
    
    # --- Тест 2: Списки зачисленных ---
    print("\n[TEST 2] generate_enrollment_lists()")
    enrolled = manager.generate_enrollment_lists()
    
    print(f"  ПМ: {len(enrolled['pm'])} зачислено")
    print(f"  ИВТ: {len(enrolled['ivt'])} зачислено")
    print(f"  ИТСС: {len(enrolled['itss'])} зачислено")
    print(f"  ИБ: {len(enrolled['ib'])} зачислено")
    
    assert len(enrolled['pm']) == 1, "На ПМ должен быть 1 зачисленный"
    assert len(enrolled['ivt']) == 2, "На ИВТ должно быть 2 зачисленных"
    assert len(enrolled['itss']) == 1, "На ИТСС должен быть 1 зачисленный"
    assert len(enrolled['ib']) == 1, "На ИБ должен быть 1 зачисленный"
    print("  ✓ Количество зачисленных корректно")
    
    # Проверяем конкретных абитуриентов
    pm_ids = [a['id'] for a in enrolled['pm']]
    ivt_ids = [a['id'] for a in enrolled['ivt']]
    itss_ids = [a['id'] for a in enrolled['itss']]
    ib_ids = [a['id'] for a in enrolled['ib']]
    
    print(f"  ПМ: ID = {pm_ids}")
    print(f"  ИВТ: ID = {ivt_ids}")
    print(f"  ИТСС: ID = {itss_ids}")
    print(f"  ИБ: ID = {ib_ids}")
    
    # Каждый абитуриент зачислен максимум в 1 программу
    all_enrolled = pm_ids + ivt_ids + itss_ids + ib_ids
    assert len(all_enrolled) == len(set(all_enrolled)), "Один абитуриент в нескольких программах!"
    print("  ✓ Каждый абитуриент зачислен только в одну программу")
    
    # --- Тест 3: Конкурсная статистика ---
    print("\n[TEST 3] calculate_competition_stats()")
    stats = manager.calculate_competition_stats()
    
    for prog, s in stats.items():
        print(f"  {s['program_name']}:")
        print(f"    Мест: {s['capacity']}, Зачислено: {s['enrolled_count']}")
        print(f"    Конкурс: {s['competition_ratio']} чел/место")
        print(f"    Статус: {s['status']}")
    
    assert stats['pm']['status'] == 'НЕДОБОР'
    assert stats['ivt']['status'] == 'НАБОР ЗАВЕРШЁН'
    assert stats['itss']['status'] == 'НАБОР ЗАВЕРШЁН'
    assert stats['ib']['status'] == 'НАБОР ЗАВЕРШЁН'
    print("  ✓ Статусы программ корректны")
    
    # --- Тест 4: Полный отчёт ---
    print("\n[TEST 4] get_statistics_report()")
    report = manager.get_statistics_report()
    
    assert 'competition' in report
    assert 'passing_score' in report
    assert 'enrolled' in report
    assert 'summary' in report
    print("  ✓ Отчёт содержит все разделы")
    
    summary = report['summary']
    print(f"  Общая сводка:")
    print(f"    Всего мест: {summary['total_capacity']}")
    print(f"    Всего зачислено: {summary['total_enrolled']}")
    print(f"    Абитуриентов с согласием: {summary['total_applicants_with_consent']}")
    print(f"    Программы с недобором: {summary['programs_with_shortage']}")
    
    assert summary['total_capacity'] == 6
    assert summary['total_enrolled'] == 5
    assert 'pm' in summary['programs_with_shortage']
    print("  ✓ Сводка корректна")
    
    print("\n" + "=" * 60)
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ ✓")
    print("=" * 60)


def test_no_consent():
    """Тест: абитуриенты без согласия не зачисляются."""
    print("\n[TEST] Абитуриенты без согласия")
    
    data = load_mock_data()
    capacity = {'pm': 10, 'ivt': 10, 'itss': 10, 'ib': 10}
    
    manager = AdmissionManager(data, capacity)
    enrolled = manager.generate_enrollment_lists()
    
    all_enrolled_ids = []
    for prog, lst in enrolled.items():
        all_enrolled_ids.extend([a['id'] for a in lst])
    
    # ID 105 имеет consent=false во всех файлах
    assert 105 not in all_enrolled_ids, "Абитуриент без согласия не должен быть зачислен"
    print("  ✓ Абитуриент 105 (consent=false) не зачислен")


if __name__ == '__main__':
    test_admission()
    test_no_consent()


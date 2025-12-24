"""
Тест класса AdmissionManager на данных из /data/mock
"""


import json
import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from admission_stats import AdmissionManager


def load_mock_data():
    """Загрузить тестовые данные из data/mock."""
    # testLogic/test_admission.py -> analysis -> src -> AdmissionAnalysis
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
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
    overall = summary['overall']
    print(f"  Общая сводка:")
    print(f"    Всего мест: {overall['total_capacity']}")
    print(f"    Всего зачислено: {overall['total_enrolled']}")
    print(f"    Абитуриентов с согласием: {overall['total_applicants_with_consent']}")
    print(f"    Программы с недобором: {overall['programs_with_shortage']}")
    
    assert overall['total_capacity'] == 6
    assert overall['total_enrolled'] == 5
    assert 'pm' in overall['programs_with_shortage']
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


def test_summary():
    """Детальный тест метода _generate_summary()."""
    print("\n" + "=" * 60)
    print("ТЕСТ SUMMARY (ТЗ)")
    print("=" * 60)
    
    data = load_mock_data()
    
    # --- Сценарий 1: Проверка структуры summary ---
    print("\n[Сценарий 1] Структура summary по ТЗ")
    capacity_1 = {'pm': 2, 'ivt': 2, 'itss': 1, 'ib': 1}
    manager_1 = AdmissionManager(data, capacity_1)
    report_1 = manager_1.get_statistics_report()
    summary_1 = report_1['summary']
    
    # Проверяем, что summary содержит нужные разделы
    assert 'programs' in summary_1, "Summary должен содержать раздел 'programs'"
    assert 'overall' in summary_1, "Summary должен содержать раздел 'overall'"
    print("  ✓ Summary содержит разделы 'programs' и 'overall'")
    
    # Проверяем статистику по программам
    print("\n  Статистика по программам:")
    for prog, stats in summary_1['programs'].items():
        print(f"\n  [{stats['program_name']}]")
        print(f"    Проходной балл: {stats['passing_score']}")
        print(f"    Мест: {stats['capacity']}, Зачислено: {stats['total_enrolled']}")
        print(f"    Всего заявлений: {stats['total_applications']}")
        print(f"    Заявления: 1пр={stats['applications_priority_1']}, "
              f"2пр={stats['applications_priority_2']}, "
              f"3пр={stats['applications_priority_3']}, "
              f"4пр={stats['applications_priority_4']}")
        print(f"    Зачислено: 1пр={stats['enrolled_priority_1']}, "
              f"2пр={stats['enrolled_priority_2']}, "
              f"3пр={stats['enrolled_priority_3']}, "
              f"4пр={stats['enrolled_priority_4']}")
        print(f"    Список зачисленных (ID): {[a['id'] for a in stats['enrolled_list']]}")
        
        # Проверки для каждой программы
        assert 'passing_score' in stats, f"У {prog} должен быть passing_score"
        assert 'capacity' in stats, f"У {prog} должно быть capacity"
        assert 'total_applications' in stats, f"У {prog} должно быть total_applications"
        assert 'enrolled_list' in stats, f"У {prog} должен быть enrolled_list"
        
        # Проверка, что сумма заявлений по приоритетам = общему числу заявлений
        apps_sum = (stats['applications_priority_1'] + stats['applications_priority_2'] +
                   stats['applications_priority_3'] + stats['applications_priority_4'])
        assert apps_sum == stats['total_applications'], \
            f"Сумма заявлений по приоритетам должна равняться общему числу для {prog}"
        
        # Проверка, что сумма зачисленных по приоритетам = общему числу зачисленных
        enr_sum = (stats['enrolled_priority_1'] + stats['enrolled_priority_2'] +
                  stats['enrolled_priority_3'] + stats['enrolled_priority_4'])
        assert enr_sum == stats['total_enrolled'], \
            f"Сумма зачисленных по приоритетам должна равняться общему числу для {prog}"
    
    print("\n  ✓ Статистика по всем программам корректна")
    
    # --- Сценарий 2: Проверка недобора ---
    print("\n[Сценарий 2] Проверка определения НЕДОБОР")
    pm_stats = summary_1['programs']['pm']
    assert pm_stats['passing_score'] == 'НЕДОБОР', "ПМ должен иметь статус НЕДОБОР"
    assert pm_stats['total_enrolled'] < pm_stats['capacity'], "Зачисленных меньше мест"
    print("  ✓ НЕДОБОР корректно определяется")
    
    # --- Сценарий 3: Проверка проходного балла ---
    print("\n[Сценарий 3] Проверка проходного балла")
    for prog, stats in summary_1['programs'].items():
        if stats['passing_score'] != 'НЕДОБОР':
            # Проверяем, что проходной балл = баллу последнего в списке
            if len(stats['enrolled_list']) > 0:
                last_score = stats['enrolled_list'][-1]['total']
                expected_score = int(stats['passing_score']) if isinstance(stats['passing_score'], (int, float)) else None
                if expected_score:
                    assert last_score == expected_score, \
                        f"Проходной балл для {prog} должен равняться баллу последнего зачисленного"
    print("  ✓ Проходные баллы соответствуют баллам последних зачисленных")
    
    # --- Сценарий 4: Общая статистика ---
    print("\n[Сценарий 4] Общая статистика")
    overall = summary_1['overall']
    print(f"  Всего мест: {overall['total_capacity']}")
    print(f"  Всего зачислено: {overall['total_enrolled']}")
    print(f"  Абитуриентов с согласием: {overall['total_applicants_with_consent']}")
    print(f"  Программы с недобором: {overall['programs_with_shortage']}")
    
    assert overall['total_capacity'] == 6, "Всего должно быть 6 мест"
    assert overall['total_enrolled'] == 5, "Зачислено должно быть 5"
    assert overall['total_applicants_with_consent'] == 5, "Должно быть 5 абитуриентов с согласием"
    assert 'pm' in overall['programs_with_shortage'], "ПМ должна быть в недоборе"
    print("  ✓ Общая статистика корректна")
    
    # --- Сценарий 5: Динамика по дням ---
    print("\n[Сценарий 5] Тест динамики по дням")
    # Создаём тестовые данные для 3 дней (с разными квотами абитуриентов)
    data_by_days = {
        '01.08': data,  # исходные данные
        '02.08': data,  # те же данные
        '03.08': data   # те же данные
    }
    
    dynamics = AdmissionManager.calculate_dynamics(data_by_days, capacity_1)
    
    print("  Динамика проходных баллов:")
    for prog, dyn in dynamics.items():
        print(f"    {dyn['program_name']}:")
        for date, score in dyn['by_date'].items():
            print(f"      {date}: {score}")
    
    assert 'pm' in dynamics, "Динамика должна содержать ПМ"
    assert 'by_date' in dynamics['pm'], "Динамика ПМ должна содержать by_date"
    assert len(dynamics['pm']['by_date']) == 3, "Должно быть 3 дня"
    print("  ✓ Динамика по дням рассчитывается корректно")
    
    print("\n" + "=" * 60)
    print("ВСЕ ТЕСТЫ SUMMARY ПРОЙДЕНЫ ✓")
    print("=" * 60)


if __name__ == '__main__':
    test_admission()
    test_no_consent()
    test_summary()
    


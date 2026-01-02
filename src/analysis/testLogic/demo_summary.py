"""
Демонстрация работы summary по требованиям ТЗ.
"""

import json
import os
import sys

# Добавляем родительскую папку в путь поиска модулей
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from admission_stats import AdmissionManager


def load_mock_data():
    """Загрузить тестовые данные из data/mock."""
    # testLogic/demo_summary.py -> analysis -> src -> AdmissionAnalysis
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    mock_dir = os.path.join(base_dir, 'data', 'mock')
    
    data = {}
    for prog in ['pm', 'ivt', 'itss', 'ib']:
        path = os.path.join(mock_dir, f'{prog}.json')
        with open(path, 'r', encoding='utf-8') as f:
            data[prog] = json.load(f)
    
    return data


def print_section(title):
    """Вывести заголовок раздела."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_single_day():
    """Демонстрация summary для одного дня."""
    print_section("ДЕМОНСТРАЦИЯ SUMMARY ПО ТРЕБОВАНИЯМ ТЗ")
    
    data = load_mock_data()
    capacity = {'pm': 2, 'ivt': 2, 'itss': 1, 'ib': 1}
    
    manager = AdmissionManager(data, capacity)
    report = manager.get_statistics_report()
    summary = report['summary']
    
    # 1. Проходные баллы на ОП
    print("\n1. ПРОХОДНЫЕ БАЛЛЫ НА ОБРАЗОВАТЕЛЬНЫЕ ПРОГРАММЫ")
    print("-" * 70)
    for prog, stats in summary['programs'].items():
        print(f"  {stats['program_name']:50} {stats['passing_score']:>15}")
    
    # 3. Списки зачисленных с ID и суммой баллов
    print("\n3. СПИСКИ ЗАЧИСЛЕННЫХ АБИТУРИЕНТОВ")
    print("-" * 70)
    for prog, stats in summary['programs'].items():
        print(f"\n  {stats['program_name']}:")
        if len(stats['enrolled_list']) == 0:
            print("    (нет зачисленных)")
        else:
            for i, applicant in enumerate(stats['enrolled_list'], 1):
                print(f"    {i}. ID: {applicant['id']:3}  |  Сумма баллов: {applicant['total']:3}  |  Приоритет: {applicant['priority']}")
    
    # 4. Детальная статистика по каждой ОП
    print("\n4. ДЕТАЛЬНАЯ СТАТИСТИКА ПО КАЖДОЙ ОБРАЗОВАТЕЛЬНОЙ ПРОГРАММЕ")
    print("-" * 70)
    for prog, stats in summary['programs'].items():
        print(f"\n  {stats['program_name']}")
        print(f"    Общее кол-во заявлений:           {stats['total_applications']}")
        print(f"    Количество мест на ОП:            {stats['capacity']}")
        print(f"    Кол-во заявлений 1-го приоритета: {stats['applications_priority_1']}")
        print(f"    Кол-во заявлений 2-го приоритета: {stats['applications_priority_2']}")
        print(f"    Кол-во заявлений 3-го приоритета: {stats['applications_priority_3']}")
        print(f"    Кол-во заявлений 4-го приоритета: {stats['applications_priority_4']}")
        print(f"    Кол-во зачисленных 1-го приоритета: {stats['enrolled_priority_1']}")
        print(f"    Кол-во зачисленных 2-го приоритета: {stats['enrolled_priority_2']}")
        print(f"    Кол-во зачисленных 3-го приоритета: {stats['enrolled_priority_3']}")
        print(f"    Кол-во зачисленных 4-го приоритета: {stats['enrolled_priority_4']}")
    
    # Общая статистика
    print("\n" + "-" * 70)
    print("ОБЩАЯ СВОДКА:")
    print(f"  Всего мест:                      {summary['overall']['total_capacity']}")
    print(f"  Всего зачислено:                 {summary['overall']['total_enrolled']}")
    print(f"  Абитуриентов с согласием:        {summary['overall']['total_applicants_with_consent']}")
    print(f"  Программы с недобором:           {', '.join(summary['overall']['programs_with_shortage']) if summary['overall']['programs_with_shortage'] else 'нет'}")


def demo_dynamics():
    """Демонстрация динамики по дням."""
    print_section("2. ДИНАМИКА ПРОХОДНОГО БАЛЛА ПО ДНЯМ")
    
    data = load_mock_data()
    capacity = {'pm': 2, 'ivt': 2, 'itss': 1, 'ib': 1}
    
    # Для демонстрации создаём данные для 4 дней (в реальности будут разные данные)
    data_by_days = {
        '01.08': data,
        '02.08': data,
        '03.08': data,
        '04.08': data
    }
    
    dynamics = AdmissionManager.calculate_dynamics(data_by_days, capacity)
    
    print("\n" + "-" * 70)
    for prog, dyn in dynamics.items():
        print(f"\n  {dyn['program_name']}:")
        for date in sorted(dyn['by_date'].keys()):
            score = dyn['by_date'][date]
            print(f"    {date}:  {score}")
    
    print("\n" + "-" * 70)
    print("  (В реальном сценарии данные за каждый день будут отличаться,")
    print("   и динамика покажет изменение проходных баллов)")


if __name__ == '__main__':
    demo_single_day()
    demo_dynamics()
    
    print("\n" + "=" * 70)
    print("  ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 70 + "\n")


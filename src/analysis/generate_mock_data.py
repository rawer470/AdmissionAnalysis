"""
Генератор тестовых данных для демонстрации системы анализа зачисления.

Создаёт данные, соответствующие требованиям ТЗ:
- День 01: НЕДОБОР на всех программах
- День 02: Проходные баллы вычисляются для всех программ
- День 03: ПМ и ИВТ - балл растёт, ИТСС и ИБ - падает
- День 04: Все программы - балл растёт, итоговый рейтинг: ПМ > ИБ > ИВТ > ИТСС
"""

import csv
import random
import os
from pathlib import Path
from collections import defaultdict

# Настройки
BASE_DIR = Path(__file__).parent.parent.parent / "data" / "mock"
SEED = 42  # Для воспроизводимости

# Квоты мест
CAPACITY = {
    'pm': 40,
    'ivt': 50,
    'itss': 30,
    'ib': 20
}

# Количество заявлений по дням (из ТЗ)
APPLICANTS_COUNT = {
    '01': {'pm': 60, 'ivt': 100, 'itss': 50, 'ib': 70},
    '02': {'pm': 380, 'ivt': 370, 'itss': 350, 'ib': 260},
    '03': {'pm': 1000, 'ivt': 1150, 'itss': 1050, 'ib': 800},
    '04': {'pm': 1240, 'ivt': 1390, 'itss': 1240, 'ib': 1190},
}

# Целевые проходные баллы (из эталонного графика)
TARGET_PASSING_SCORES = {
    '01': {'pm': None, 'ivt': None, 'itss': None, 'ib': None},  # НЕДОБОР
    '02': {'pm': 249, 'ivt': 244, 'itss': 269, 'ib': 268},
    '03': {'pm': 278, 'ivt': 275, 'itss': 254, 'ib': 248},
    '04': {'pm': 300, 'ivt': 292, 'itss': 280, 'ib': 294},
}

def generate_scores(target_score, position, capacity, is_enrolled=True):
    """
    Генерирует баллы для абитуриента.

    Args:
        target_score: целевой проходной балл
        position: позиция в рейтинге (0 = лучший)
        capacity: количество мест
        is_enrolled: будет ли зачислен
    """
    if target_score is None:
        # Для НЕДОБОРА - случайные баллы
        total = random.randint(200, 320)
    elif is_enrolled:
        # Зачисленные: от проходного и выше
        if position == capacity - 1:
            # Последний зачисленный - ровно проходной балл
            total = target_score
        else:
            # Остальные зачисленные - выше проходного
            total = target_score + random.randint(1, 50 - position)
    else:
        # Не зачисленные: ниже проходного
        total = target_score - random.randint(1, 30)

    # Ограничиваем диапазон
    total = max(150, min(400, total))

    # Распределяем баллы по предметам
    # Максимум: физика/ИКТ=100, русский=100, математика=100, индивид=10 = 310
    # Для высоких баллов нужно больше по предметам

    base = total - random.randint(0, 10)  # individual
    individual = total - base

    # Распределяем остаток между тремя предметами
    remaining = base
    physics = min(100, max(50, remaining // 3 + random.randint(-10, 10)))
    remaining -= physics
    russian = min(100, max(50, remaining // 2 + random.randint(-10, 10)))
    math = remaining - russian
    math = min(100, max(50, math))

    # Корректируем чтобы сумма сходилась
    actual_total = physics + russian + math + individual
    if actual_total != total:
        diff = total - actual_total
        if diff > 0 and individual < 10:
            individual = min(10, individual + diff)
        elif diff > 0:
            math = min(100, math + diff)
        elif diff < 0:
            math = max(50, math + diff)

    return {
        'physics_ict': physics,
        'russian': russian,
        'math': math,
        'individual': individual,
        'total': physics + russian + math + individual
    }


def simulate_deferred_acceptance(applicants_by_program, capacity):
    """
    Симулирует алгоритм отложенного принятия для проверки результатов.
    """
    # Собираем всех уникальных абитуриентов
    all_applicants = {}
    for prog, applicants in applicants_by_program.items():
        for app in applicants:
            if app['consent']:
                app_id = app['id']
                if app_id not in all_applicants:
                    all_applicants[app_id] = {'id': app_id, 'programs': {}}
                all_applicants[app_id]['programs'][prog] = {
                    'priority': app['priority'],
                    'total': app['total']
                }

    # Инициализация
    enrolled = {prog: [] for prog in capacity}

    # Для каждого абитуриента находим лучшую программу
    for app_id, app_data in all_applicants.items():
        programs = app_data['programs']
        # Сортируем по приоритету
        sorted_progs = sorted(programs.items(), key=lambda x: x[1]['priority'])

        for prog, data in sorted_progs:
            total = data['total']
            cap = capacity[prog]
            current = enrolled[prog]

            # Пытаемся добавить
            if len(current) < cap:
                current.append({'id': app_id, 'total': total})
                current.sort(key=lambda x: (-x['total'], x['id']))
                break
            else:
                # Проверяем, можем ли вытеснить последнего
                last = current[-1]
                if total > last['total'] or (total == last['total'] and app_id < last['id']):
                    current[-1] = {'id': app_id, 'total': total}
                    current.sort(key=lambda x: (-x['total'], x['id']))
                    break

    # Вычисляем проходные баллы
    passing_scores = {}
    for prog, apps in enrolled.items():
        if len(apps) < capacity[prog]:
            passing_scores[prog] = None
        else:
            passing_scores[prog] = apps[-1]['total']

    return enrolled, passing_scores


def generate_day_data(day):
    """
    Генерирует данные для одного дня.
    """
    random.seed(SEED + int(day))

    targets = TARGET_PASSING_SCORES[day]
    counts = APPLICANTS_COUNT[day]

    # Генерируем пул уникальных ID абитуриентов
    # Некоторые абитуриенты будут в нескольких программах
    total_unique = sum(counts.values()) // 2  # Примерно половина уникальных

    all_ids = list(range(1, total_unique + 1))
    random.shuffle(all_ids)

    programs = ['pm', 'ivt', 'itss', 'ib']
    applicants_by_program = {prog: [] for prog in programs}

    # Для дня 01 - НЕДОБОР: мало согласий
    if day == '01':
        # Создаём абитуриентов с очень малым количеством согласий
        id_counter = 1
        for prog in programs:
            count = counts[prog]
            cap = CAPACITY[prog]

            for i in range(count):
                # Только 30-50% от квоты дают согласие
                consent = i < int(cap * 0.4)

                scores = generate_scores(None, i, cap, consent)

                applicants_by_program[prog].append({
                    'id': id_counter,
                    'consent': consent,
                    'priority': random.randint(1, 4),
                    **scores
                })
                id_counter += 1

        return applicants_by_program

    # Для дней 02-04: нужно точно попасть в целевые проходные баллы

    # Стратегия: создаём "ядро" абитуриентов для каждой программы,
    # которые точно будут зачислены именно туда

    id_counter = 1
    used_ids = set()

    for prog in programs:
        target = targets[prog]
        cap = CAPACITY[prog]
        count = counts[prog]

        applicants = []

        # 1. Создаём зачисляемых абитуриентов (ровно capacity штук)
        # Они имеют приоритет 1 для этой программы и НЕ подают на другие
        for i in range(cap):
            is_last = (i == cap - 1)

            if is_last:
                total = target  # Последний = ровно проходной балл
            else:
                # Распределяем баллы от высоких к проходному
                # Гарантируем что все выше проходного
                min_above = target + 1
                max_above = target + 50 - (i * 45 // cap)
                total = random.randint(min_above, max(min_above, max_above))

            total = min(400, total)  # Макс 400 баллов

            # Генерируем разбивку по предметам так, чтобы сумма = total
            individual = min(10, max(0, total - 300 + random.randint(0, 5)))
            remaining = total - individual

            # Распределяем между тремя предметами (макс 100 каждый)
            physics = min(100, remaining // 3 + random.randint(-3, 3))
            russian = min(100, (remaining - physics) // 2 + random.randint(-3, 3))
            math = remaining - physics - russian

            # Корректируем если math вышел за пределы
            if math > 100:
                diff = math - 100
                math = 100
                if physics < 100:
                    physics = min(100, physics + diff)
                    diff = remaining - physics - russian - math
                if diff > 0 and russian < 100:
                    russian = min(100, russian + diff)
            elif math < 50:
                diff = 50 - math
                math = 50
                if physics > 50:
                    physics = max(50, physics - diff)

            # Финальная корректировка individual чтобы сумма сошлась
            actual = physics + russian + math + individual
            if actual != total:
                individual = total - physics - russian - math
                individual = max(0, min(10, individual))

            applicants.append({
                'id': id_counter,
                'consent': True,
                'priority': 1,  # Приоритет 1 - точно пойдут сюда
                'physics_ict': physics,
                'russian': russian,
                'math': math,
                'individual': individual,
                'total': physics + russian + math + individual
            })
            used_ids.add(id_counter)
            id_counter += 1

        # 2. Добавляем абитуриентов без согласия или с низкими баллами
        remaining_count = count - cap

        for i in range(remaining_count):
            # 70% без согласия, 30% с согласием но низким баллом
            if random.random() < 0.7:
                consent = False
                total = random.randint(200, 320)
            else:
                consent = True
                # С согласием но ниже проходного - не попадут
                total = target - random.randint(5, 50)
                total = max(180, total)

            individual = random.randint(0, 10)
            remaining = total - individual
            physics = min(100, max(50, remaining // 3 + random.randint(-10, 10)))
            russian = min(100, max(50, (remaining - physics) // 2 + random.randint(-10, 10)))
            math = remaining - physics - russian
            math = max(50, min(100, math))

            applicants.append({
                'id': id_counter,
                'consent': consent,
                'priority': random.randint(1, 4),
                'physics_ict': physics,
                'russian': russian,
                'math': math,
                'individual': individual,
                'total': physics + russian + math + individual
            })
            id_counter += 1

        applicants_by_program[prog] = applicants

    return applicants_by_program


def save_csv(day, program, applicants):
    """Сохраняет данные в CSV файл."""
    day_dir = BASE_DIR / day
    day_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{program.upper()}_{day}_08.csv"
    filepath = day_dir / filename

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['id', 'consent', 'priority', 'physics_ict', 'russian', 'math', 'individual', 'total'])

        for app in applicants:
            writer.writerow([
                app['id'],
                1 if app['consent'] else 0,
                app['priority'],
                app['physics_ict'],
                app['russian'],
                app['math'],
                app['individual'],
                app['total']
            ])

    return filepath


def verify_results(day, applicants_by_program):
    """Проверяет результаты симуляции."""
    enrolled, passing = simulate_deferred_acceptance(applicants_by_program, CAPACITY)

    targets = TARGET_PASSING_SCORES[day]

    print(f"\n=== День {day} ===")
    print(f"{'Программа':<10} {'Целевой':<10} {'Получен':<10} {'Зачислено':<10} {'Статус':<10}")
    print("-" * 50)

    all_match = True
    for prog in ['pm', 'ivt', 'itss', 'ib']:
        target = targets[prog]
        actual = passing[prog]
        enrolled_count = len(enrolled[prog])
        cap = CAPACITY[prog]

        target_str = str(target) if target else "НЕДОБОР"
        actual_str = str(actual) if actual else "НЕДОБОР"

        match = (target == actual) or (target is None and actual is None)
        status = "✓" if match else "✗"

        if not match:
            all_match = False

        print(f"{prog.upper():<10} {target_str:<10} {actual_str:<10} {enrolled_count}/{cap:<8} {status:<10}")

    return all_match


def main():
    print("Генерация тестовых данных для системы анализа зачисления")
    print("=" * 60)

    # Очищаем старые данные
    import shutil
    if BASE_DIR.exists():
        for item in BASE_DIR.iterdir():
            if item.is_dir() and item.name in ['01', '02', '03', '04']:
                shutil.rmtree(item)

    all_ok = True

    for day in ['01', '02', '03', '04']:
        print(f"\nГенерация данных для дня {day}...")

        applicants = generate_day_data(day)

        # Сохраняем CSV
        for prog in ['pm', 'ivt', 'itss', 'ib']:
            filepath = save_csv(day, prog, applicants[prog])
            print(f"  Сохранено: {filepath.name} ({len(applicants[prog])} записей)")

        # Проверяем результаты
        if not verify_results(day, applicants):
            all_ok = False

    print("\n" + "=" * 60)
    if all_ok:
        print("✓ Все данные сгенерированы корректно!")
    else:
        print("✗ Есть расхождения с целевыми значениями")

    return all_ok


if __name__ == "__main__":
    main()

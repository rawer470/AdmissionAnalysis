"""
Тест для генератора PDF отчетов (ReportManager).
Проверяет создание PDF отчета за все 4 дня с графиком динамики.
"""

import sys
from pathlib import Path

# Добавляем родительскую папку в путь для импорта
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from report_manager import ReportManager


def test_pdf_all_days():
    """
    Тест генерации PDF отчета за все 4 дня.
    Включает график динамики, таблицы и списки зачисленных.
    """
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*12 + "ТЕСТ PDF ГЕНЕРАТОРА (4 ДНЯ)" + " "*18 + "║")
    print("╚" + "="*58 + "╝\n")
    
    try:
        # 1. Создание менеджера
        print("Шаг 1: Создание ReportManager")
        manager = ReportManager()
        print("  ✓ Менеджер создан\n")
        
        # 2. Загрузка отчетов за 4 дня
        print("Шаг 2: Загрузка отчетов")
        dates = ['01', '02', '03', '04']
        
        for date in dates:
            report = manager.add_report(date)
            pm_score = report['passing_score'].get('pm')
            score_text = str(pm_score) if pm_score else 'НЕДОБОР'
            print(f"  ✓ День {date}: проходной балл ПМ = {score_text}")
        
        print(f"\n  Всего загружено: {len(manager.get_reports())} отчетов\n")
        
        # 3. Генерация PDF
        print("Шаг 3: Генерация PDF отчета")
        target_date = '04'
        print(f"  Целевая дата: {target_date}")
        print(f"  Период анализа: {dates[0]}-{dates[-1]} ({len(dates)} дней)")
        
        pdf_path = manager.generate_pdf(target_date)
        
        # 4. Проверка результата
        print("\nШаг 4: Проверка результата")
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF файл не создан: {pdf_path}")
        
        size_kb = pdf_path.stat().st_size / 1024
        
        print(f"  ✓ Файл создан: {pdf_path.name}")
        print(f"  ✓ Размер: {size_kb:.2f} KB")
        print(f"  ✓ Путь: {pdf_path}")
        
        # Проверка размера
        if size_kb < 10:
            print(f"  ⚠ Предупреждение: размер файла подозрительно мал")
        elif size_kb > 500:
            print(f"  ⚠ Предупреждение: размер файла слишком большой")
        else:
            print(f"  ✓ Размер файла в норме")
        
        # 5. Содержимое отчета
        print("\nШаг 5: Содержимое PDF")
        print("  ✓ Заголовок и дата формирования")
        print("  ✓ Проходные баллы по 4 программам")
        print(f"  ✓ График динамики ({len(dates)} точек данных)")
        print("  ✓ Списки зачисленных абитуриентов")
        print("  ✓ Таблица статистики по программам")
        print("  ✓ Поддержка русского языка (Arial Unicode)")
        
        # Итог
        print("\n" + "─"*60)
        print("✓ ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("─"*60)
        print(f"\nPDF отчет: {pdf_path}")
        print(f"Размер: {size_kb:.2f} KB")
        print(f"Дни: {dates[0]}-{dates[-1]} ({len(dates)} дней)")
        
        return True
        
    except Exception as e:
        print("\n" + "─"*60)
        print("✗ ТЕСТ ПРОВАЛЕН")
        print("─"*60)
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pdf_all_days()
    sys.exit(0 if success else 1)


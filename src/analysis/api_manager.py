"""
FastAPI сервис для анализа зачисления абитуриентов.
Обрабатывает загруженные таблицы из папки uploads.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
from pathlib import Path
import csv
import os
import datetime
import io
import matplotlib.pyplot as mplt
import reportlab.platypus
import reportlab.lib.colors
import reportlab.lib.pagesizes
import reportlab.lib.styles
import reportlab.pdfbase.pdfmetrics
import reportlab.pdfbase.ttfonts

from admission_stats import AdmissionManager




# ===================== Настройки путей =====================

# Базовая папка с данными
BASE_DIR = Path(__file__).parent.parent.parent / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
MOCK_DIR = BASE_DIR / "mock"
# Квоты мест (по умолчанию)
DEFAULT_CAPACITY = {
    'pm': 40,
    'ivt': 50,
    'itss': 30,
    'ib': 20
}


# ===================== Инициализация FastAPI =====================

app = FastAPI(
    title="AdmissionAnalysis API",
    description="API для анализа зачисления абитуриентов",
    version="1.0.0"
)

# CORS для интеграции с ASP.NET
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================== Вспомогательные функции =====================

def load_csv_from_uploads(date_folder: str) -> Dict[str, list]:
    """
    Загружает CSV файлы из папки uploads/date_folder.
    
    Ожидаемые файлы:
        - PM.csv, IVT.csv, ITSS.csv, IB.csv
    или
        - date_PM.csv, date_IVT.csv и т.д.
    """
    #ДЛЯ РЕАЛЬНОГО ТЕСТА
    #upload_path = UPLOADS_DIR / date_folder

    #ДЛЯ МОК ТЕСТА
    upload_path = MOCK_DIR / date_folder
    
    if not upload_path.exists():
        raise FileNotFoundError(f"Папка {date_folder} не найдена в uploads")
    
    data = {}
    program_codes = {'pm': 'PM', 'ivt': 'IVT', 'itss': 'ITSS', 'ib': 'IB'}
    
    for code, file_prefix in program_codes.items():
        # Ищем файл по паттерну
        csv_files = list(upload_path.glob(f"*{file_prefix}*.csv"))
        
        if not csv_files:
            continue
        
        csv_file = csv_files[0]  # берём первый найденный
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            applicants = []
            
            for row in reader:
                # Поддержка обоих форматов: physicsIct и physics_ict
                physics_ict = row.get('physicsIct') or row.get('physics_ict', 0)
                
                # consent может быть 1/0 или true/false
                consent_val = row['consent']
                if consent_val in ['1', 'true', 'True', 'TRUE']:
                    consent = True
                else:
                    consent = False
                
                applicants.append({
                    'id': int(row['id']),
                    'consent': consent,
                    'priority': int(row['priority']),
                    'total': int(row['total']),
                    'math': int(row.get('math', 0)),
                    'russian': int(row.get('russian', 0)),
                    'physicsIct': int(physics_ict),
                    'individual': int(row.get('individual', 0))
                })
            
            data[code] = applicants
    
    return data


# ===================== Endpoints =====================

@app.get("/")
def root():
    """Корневой endpoint."""
    return {
        "status": "ok",
        "service": "AdmissionAnalysis API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Проверка работоспособности."""
    return {"status": "healthy"}


@app.get("/api/analyze/{date_folder}")
def analyze_uploads(
    date_folder: str,
    capacity_pm: Optional[int] = 40,
    capacity_ivt: Optional[int] = 50,
    capacity_itss: Optional[int] = 30,
    capacity_ib: Optional[int] = 20
) -> Dict[str, Any]:
    """
    Анализирует загруженные таблицы из папки uploads/{date_folder}.
    
    Процесс:
        1. Читает CSV файлы из uploads/{date_folder}
        2. Выполняет анализ зачисления
        3. Возвращает результат
    
    Args:
        date_folder: имя папки с данными (например: "01-08", "2024-08-01")
        capacity_pm: места на ПМ (по умолчанию 40)
        capacity_ivt: места на ИВТ (по умолчанию 50)
        capacity_itss: места на ИТСС (по умолчанию 30)
        capacity_ib: места на ИБ (по умолчанию 20)
    """
    try:
        # 1. Загружаем данные из uploads
        applicants_data = load_csv_from_uploads(date_folder)
        
        if not applicants_data:
            raise ValueError(f"Не найдены CSV файлы в папке {date_folder}")
        
        # 2. Квоты мест
        capacity = {
            'pm': capacity_pm,
            'ivt': capacity_ivt,
            'itss': capacity_itss,
            'ib': capacity_ib
        }
        
        # 3. Анализ
        manager = AdmissionManager(applicants_data, capacity)
        report = manager.get_statistics_report()
        generate_pdf_report(report)
        
        # 4. Возвращаем результат
        return {
            "success": True,
            "date_folder": date_folder,
            "files_processed": list(applicants_data.keys()),
            "data": report
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка анализа: {str(e)}")


@app.get("/api/uploads")
def list_uploads() -> Dict[str, Any]:
    """
    Список папок в директории uploads.
    """
    try:
        if not UPLOADS_DIR.exists():
            return {"success": True, "folders": []}
        
        folders = [f.name for f in UPLOADS_DIR.iterdir() if f.is_dir()]
        folders.sort()
        
        return {
            "success": True,
            "folders": folders,
            "count": len(folders)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/programs")
def get_programs() -> Dict[str, Any]:
    """Список образовательных программ."""
    return {
        "success": True,
        "data": AdmissionManager.PROGRAM_NAMES
    }


def generate_pdf_report(report):
    """
    Генерирует PDF отчет.
    Использует полные пути к библиотекам (без from ... import func).
    """
    # === 1. Подготовка файла и шрифтов ===
    reports_dir = BASE_DIR / "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    filename = f"report_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    file_path = reports_dir / filename

    # Регистрируем шрифт (ищем .ttf, иначе fallback)
    font_name = 'Helvetica' # Дефолтный шрифт (не поддерживает кириллицу)
    # Список шрифтов для перебора (должен лежать рядом с api_manager.py)
    search_fonts = ['arial.ttf', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf']
    for font in search_fonts:
        try:
            # Обращение через полный путь к модулю
            font_obj = reportlab.pdfbase.ttfonts.TTFont('CustomFont', font)
            reportlab.pdfbase.pdfmetrics.registerFont(font_obj)
            font_name = 'CustomFont'
            break
        except:
            continue

    # === 2. Настройка документа ===
    doc = reportlab.platypus.SimpleDocTemplate(
        str(file_path), 
        pagesize=reportlab.lib.pagesizes.A4
    )
    story = []
    
    # Получаем стили через модуль styles
    styles_obj = reportlab.lib.styles.getSampleStyleSheet()
    style_h = styles_obj['Heading2']
    style_h.fontName = font_name
    style_n = styles_obj['Normal']
    style_n.fontName = font_name

    # === 3. Формирование контента ===
    
    # --- a. Дата ---
    date_str = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
    story.append(reportlab.platypus.Paragraph(f"Отчет от: {date_str}", style_n))
    story.append(reportlab.platypus.Spacer(1, 10))

    # --- b. Проходные баллы ---
    story.append(reportlab.platypus.Paragraph("Проходные баллы:", style_h))
    
    progs = ['pm', 'ivt', 'itss', 'ib']
    prog_map = {'pm': 'ПМ', 'ivt': 'ИВТ', 'itss': 'ИТСС', 'ib': 'ИБ'}
    
    txt_parts = []
    for p in progs:
        val = report['passing_score'].get(p)
        val_str = str(val) if val is not None else 'НЕДОБОР'
        txt_parts.append(f"<b>{prog_map[p]}</b>: {val_str}")
        
    story.append(reportlab.platypus.Paragraph("; ".join(txt_parts), style_n))
    story.append(reportlab.platypus.Spacer(1, 15))

    # --- c. Графики (matplotlib) ---
    story.append(reportlab.platypus.Paragraph("Динамика (4 дня):", style_h))
    
    try:
        # Определяем папку с данными
        src = MOCK_DIR if os.path.exists(MOCK_DIR) else UPLOADS_DIR
        # Ищем 4 последние папки
        all_dirs = sorted([d.name for d in src.iterdir() if d.is_dir()])
        last_dates = all_dirs[-4:]
        
        if last_dates:
            # Загружаем данные
            hist_data = {}
            for d in last_dates:
                try:
                    hist_data[d] = load_csv_from_uploads(d)
                except: pass
            
            # Считаем
            dyn = AdmissionManager.calculate_dynamics(hist_data, DEFAULT_CAPACITY)
            
            # Рисуем через mplt
            mplt.figure(figsize=(7, 3.5))
            for p in progs:
                dates_x = []
                vals_y = []
                p_data = dyn.get(p, {}).get('by_date', {})
                
                for d_key in sorted(p_data.keys()):
                    sc = p_data[d_key]
                    if sc != 'НЕДОБОР':
                        dates_x.append(d_key)
                        vals_y.append(sc)
                
                if dates_x:
                    mplt.plot(dates_x, vals_y, marker='o', label=prog_map[p])
            
            mplt.grid(True)
            mplt.legend()
            
            # Сохраняем в буфер
            buf = io.BytesIO()
            mplt.savefig(buf, format='png')
            buf.seek(0)
            mplt.close()
            
            # Вставляем Image из platypus
            story.append(reportlab.platypus.Image(buf, width=450, height=220))
    except Exception as e:
        story.append(reportlab.platypus.Paragraph(f"Ошибка графика: {e}", style_n))

    story.append(reportlab.platypus.PageBreak())

    # --- e. Сводная таблица ---
    story.append(reportlab.platypus.Paragraph("Статистика:", style_h))
    
    # Структура строк (Название, Ключ в словаре)
    rows_map = [
        ('Общее кол-во заявлений', 'total_applications'),
        ('Количество мест на ОП ', 'capacity'),
        ('Кол-во заявлений 1-го приоритета', 'applications_priority_1'),
        ('Кол-во заявлений 2-го приоритета', 'applications_priority_2'),
        ('Кол-во заявлений 3-го приоритета', 'applications_priority_3'),
        ('Кол-во заявлений 4-го приоритета', 'applications_priority_4'),
        ('Зачислено Приоритет 1', 'enrolled_priority_1'),
        ('Зачислено Приоритет 2', 'enrolled_priority_2'),
        ('Зачислено Приоритет 3', 'enrolled_priority_3'),
        ('Зачислено Приоритет 4', 'enrolled_priority_4'),
    ]

    # Заголовок
    t_data = [[''] + [prog_map[p] for p in progs]]
    
    # Данные
    r_stats = report['summary']['programs']
    for label, key in rows_map:
        row = [label]
        for p in progs:
            row.append(str(r_stats[p].get(key, 0)))
        t_data.append(row)

    # Создание таблицы
    table = reportlab.platypus.Table(t_data, colWidths=[155, 60, 60, 60, 60])
    
    # Стиль таблицы
    ts = reportlab.platypus.TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 1, reportlab.lib.colors.black),
        ('BACKGROUND', (0,0), (-1,0), reportlab.lib.colors.lightgrey),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ])
    table.setStyle(ts)
    story.append(table)
    story.append(reportlab.platypus.Spacer(1, 15))

    # --- d. Списки зачисленных ---
    story.append(reportlab.platypus.Paragraph("Списки зачисленных:", style_h))
    
    for p in progs:
        enr = report['enrolled'][p]
        if not enr:
            continue
            
        story.append(reportlab.platypus.Paragraph(f"Программа {prog_map[p]}:", style_n))
        
        # Данные для списка
        l_data = [['ID', 'Балл']]
        for student in enr:
            l_data.append([str(student['id']), str(student['total'])])
            
        l_table = reportlab.platypus.Table(l_data, colWidths=[100, 60], hAlign='LEFT')
        l_table.setStyle(reportlab.platypus.TableStyle([
            ('FONTNAME', (0,0), (-1,-1), font_name),
            ('GRID', (0,0), (-1,-1), 1, reportlab.lib.colors.black),
            ('BACKGROUND', (0,0), (1,0), reportlab.lib.colors.lightgrey),
        ]))
        story.append(l_table)
        story.append(reportlab.platypus.Spacer(1, 10))

    # Генерация
    doc.build(story)
    return str(file_path)
        


# ===================== Запуск =====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api_manager:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )


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
from report_manager import ReportManager




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
        report = manager.get_statistics_report(
            date_folder=date_folder,
            save_to_reports=True  # Сохранить stats.json в reports/{date_folder}/
        )
      
        
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




@app.get("/api/generate_pdf_report")
def generate_pdf_report(
    date_folders: Optional[str] = None,
    target_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Генерирует PDF отчет о зачислении.
    
    Args:
        date_folders: список папок с датами через запятую (например: "01,02,03,04")
                     Если не указано, загружаются все доступные отчеты
        target_date: целевая дата для отчета (например: "04")
                    Если не указано, используется последняя дата из списка
    
    Returns:
        JSON с информацией о созданном PDF файле
        
    Example:
        GET /api/generate_pdf_report?date_folders=01,02,03,04&target_date=04
        GET /api/generate_pdf_report  (автоматически найдет все отчеты)
    """
    try:
        report_manager = ReportManager()
        
        # Определяем список дат для загрузки
        if date_folders:
            # Используем указанные даты
            folders = [d.strip() for d in date_folders.split(',')]
        else:
            # Автоматически находим все доступные отчеты
            reports_dir = BASE_DIR / "reports"
            if not reports_dir.exists():
                raise ValueError("Папка reports не найдена")
            
            folders = []
            for item in reports_dir.iterdir():
                if item.is_dir() and (item / "stats.json").exists():
                    folders.append(item.name)
            
            if not folders:
                raise ValueError("Не найдено отчетов для генерации PDF")
            
            folders.sort()
        
        # Загружаем отчеты
        loaded_count = 0
        errors = []
        for folder in folders:
            try:
                report_manager.add_report(folder)
                loaded_count += 1
            except Exception as e:
                errors.append(f"{folder}: {str(e)}")
        
        if loaded_count == 0:
            raise ValueError(f"Не удалось загрузить ни одного отчета. Ошибки: {'; '.join(errors)}")
        
        # Определяем целевую дату
        if not target_date:
            target_date = folders[-1]  # Используем последнюю дату
        
        # Генерируем PDF
        pdf_path = report_manager.generate_pdf(target_date)
        
        return {
            "success": True,
            "message": "PDF отчет успешно сгенерирован",
            "data": {
                "pdf_path": str(pdf_path),
                "filename": pdf_path.name,
                "size_kb": round(pdf_path.stat().st_size / 1024, 2),
                "dates_included": folders,
                "target_date": target_date,
                "reports_loaded": loaded_count
            },
            "errors": errors if errors else None
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")


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

# ===================== Запуск =====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api_manager:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )


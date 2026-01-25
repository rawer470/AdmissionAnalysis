import os
import json
import datetime
import io
from pathlib import Path

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from matplotlib import pyplot as plt
import matplotlib
import matplotlib.font_manager as fm

# Настройка matplotlib для работы без GUI
matplotlib.use('Agg')

# ===================== Настройки путей =====================
# Базовая папка с данными
BASE_DIR = Path(__file__).parent.parent.parent / "data"

# Настройка русского шрифта для matplotlib
plt.rcParams['axes.unicode_minus'] = False

# Регистрация русского шрифта для ReportLab и matplotlib
RUSSIAN_FONT = 'ArialUnicode'
RUSSIAN_FONT_BOLD = 'ArialUnicode'

try:
    # Ищем Arial Unicode (есть на macOS, поддерживает кириллицу)
    arial_unicode_path = None
    arial_path = None
    
    for font_path in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
        if 'Arial Unicode.ttf' in font_path:
            arial_unicode_path = font_path
        elif 'Arial.ttf' in font_path and 'Bold' not in font_path and 'Italic' not in font_path:
            arial_path = font_path
    
    # Регистрируем Arial Unicode для ReportLab
    if arial_unicode_path:
        pdfmetrics.registerFont(TTFont('ArialUnicode', arial_unicode_path))
        RUSSIAN_FONT = 'ArialUnicode'
        RUSSIAN_FONT_BOLD = 'ArialUnicode'
        plt.rcParams['font.family'] = 'Arial Unicode MS'
    elif arial_path:
        # Используем обычный Arial
        pdfmetrics.registerFont(TTFont('ArialUnicode', arial_path))
        RUSSIAN_FONT = 'ArialUnicode'
        RUSSIAN_FONT_BOLD = 'ArialUnicode'
        plt.rcParams['font.family'] = 'Arial'
    else:
        # Если не нашли, используем стандартный (без кириллицы)
        RUSSIAN_FONT = 'Helvetica'
        RUSSIAN_FONT_BOLD = 'Helvetica-Bold'
        
except Exception as e:
    # Если не получилось, используем стандартный шрифт
    RUSSIAN_FONT = 'Helvetica'
    RUSSIAN_FONT_BOLD = 'Helvetica-Bold'


class ReportManager:
    """
    Менеджер для управления отчетами о зачислении.
    Загружает данные из stats.json и хранит их в памяти.
    """

    def __init__(self):
        """Инициализация менеджера отчетов."""
        self.reports = []
        self._reports_by_date = {}

    def add_report(self, date_folder):
        """
        Добавить отчет в список по дате.
        Загружает данные из stats.json для указанной папки.

        Args:
            date_folder: название папки с датой (например "01", "04", "2024-08-01")

        Returns:
            dict: загруженный отчет с данными из stats.json

        Raises:
            FileNotFoundError: если stats.json не найден
            ValueError: если ошибка чтения JSON
        """
        # Проверяем, не загружен ли уже этот отчет
        if date_folder in self._reports_by_date:
            return self._reports_by_date[date_folder]

        # Путь к stats.json
        # BASE_DIR = /path/to/AdmissionAnalysis/data
        stats_path = BASE_DIR / "reports" / date_folder / "stats.json"

        # Читаем stats.json
        if not stats_path.exists():
            raise FileNotFoundError(f"Файл stats.json не найден: {stats_path}")

        try:
            with open(stats_path, "r", encoding="utf-8") as f:
                stats_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка чтения stats.json для {date_folder}: {e}")

        # Создаем отчет
        report = {
            "date_folder": date_folder,
            "competition": stats_data.get("competition", {}),
            "passing_score": stats_data.get("passing_score", {}),
            "enrolled": stats_data.get("enrolled", {}),
            "summary": stats_data.get("summary", {}),
            "metadata": stats_data.get("_metadata", {}),
            "loaded_at": datetime.datetime.now().isoformat(),
        }

        # Сохраняем в список и словарь
        self.reports.append(report)
        self._reports_by_date[date_folder] = report

        return report

    def get_reports(self):
        """
        Получить список всех добавленных отчетов.

        Returns:
            list: список отчетов
        """
        return self.reports

    def get_report_by_date(self, date_folder):
        """
        Получить отчет по дате.

        Args:
            date_folder: название папки с датой

        Returns:
            dict или None: отчет или None если не найден
        """
        return self._reports_by_date.get(date_folder)

    def clear_reports(self):
        """Очистить все отчеты из памяти."""
        self.reports.clear()
        self._reports_by_date.clear()

    def load_multiple_reports(self, date_folders):
        """
        Загрузить несколько отчетов за раз.

        Args:
            date_folders: список папок с датами

        Returns:
            dict: словарь {date_folder: report} для успешно загруженных,
                  {date_folder: error_message} для неудачных
        """
        results = {}
        for date_folder in date_folders:
            try:
                report = self.add_report(date_folder)
                results[date_folder] = {"success": True, "report": report}
            except Exception as e:
                results[date_folder] = {"success": False, "error": str(e)}

        return results

    def generate_pdf(self, date_folder=None, filename=None):
        """
        Генерация PDF отчета о зачислении.
        Отчет формируется с учетом всех загруженных дат (динамика).
        
        Args:
            date_folder: опциональная папка с датой (используется для получения основного отчета)
            filename: опциональное имя файла (по умолчанию report_{timestamp}.pdf)
            
        Returns:
            Path: путь к созданному PDF файлу
        """
        # Если не указан date_folder, используем последний загруженный отчет
        if date_folder is None:
            if not self.reports:
                raise ValueError("Нет загруженных отчетов")
            # Используем последний отчет
            report = self.reports[-1]
            date_folder = report['date_folder']
        else:
            report = self.get_report_by_date(date_folder)
            if not report:
                raise ValueError(f"Отчет за дату {date_folder} не найден")
        
        # Путь к общей папке reports (не в подпапку с датой)
        reports_dir = BASE_DIR / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Имя файла
        if filename is None:
            # Формируем имя с диапазоном дат если загружено несколько отчетов
            if len(self.reports) > 1:
                sorted_dates = sorted([r['date_folder'] for r in self.reports])
                date_range = f"{sorted_dates[0]}-{sorted_dates[-1]}"
                filename = f"report_{date_range}.pdf"
            else:
                filename = f"report_{date_folder}.pdf"
        
        pdf_path = reports_dir / filename
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Создаем PDF документ
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        # Стили с поддержкой русского языка
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=RUSSIAN_FONT_BOLD,
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=RUSSIAN_FONT_BOLD,
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=RUSSIAN_FONT,
            fontSize=11
        )
        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading3'],
            fontName=RUSSIAN_FONT_BOLD,
            fontSize=13
        )
        italic_style = ParagraphStyle(
            'CustomItalic',
            parent=styles['Italic'],
            fontName=RUSSIAN_FONT,
            fontSize=10
        )
        
        # Контент документа
        content = []
        
        # a. Дата и время формирования отчета
        content.append(Paragraph("ОТЧЕТ О ЗАЧИСЛЕНИИ АБИТУРИЕНТОВ", title_style))
        current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        content.append(Paragraph(f"Дата формирования: {current_time}", normal_style))
        
        # Показываем период с учетом всех загруженных дат
        if len(self.reports) > 1:
            sorted_dates = sorted([r['date_folder'] for r in self.reports])
            period_text = f"Период анализа: дни {sorted_dates[0]}-{sorted_dates[-1]} ({len(self.reports)} дней)"
        else:
            period_text = f"Период анализа: день {date_folder}"
        
        content.append(Paragraph(period_text, normal_style))
        content.append(Paragraph(f"Данные на дату: {date_folder}", normal_style))
        content.append(Spacer(1, 20))
        
        # b. Проходные баллы
        content.append(Paragraph("ПРОХОДНЫЕ БАЛЛЫ", heading_style))
        passing_scores = report.get('passing_score', {})
        program_names = {
            'pm': 'Прикладная математика',
            'ivt': 'Информатика и вычислительная техника',
            'itss': 'Инфокоммуникационные технологии и системы связи',
            'ib': 'Информационная безопасность'
        }
        
        passing_data = [['Программа', 'Проходной балл']]
        for code, name in program_names.items():
            score = passing_scores.get(code)
            score_text = str(score) if score is not None else "НЕДОБОР"
            passing_data.append([name, score_text])
        
        passing_table = Table(passing_data, colWidths=[4*inch, 1.5*inch])
        passing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3f51b5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
            ('FONTNAME', (0, 0), (-1, 0), RUSSIAN_FONT_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        content.append(passing_table)
        content.append(Spacer(1, 20))
        
        # c. Динамика проходного балла (графики)
        if len(self.reports) > 1:
            content.append(Paragraph("ДИНАМИКА ПРОХОДНЫХ БАЛЛОВ", heading_style))
            chart_img = self._create_dynamics_chart()
            if chart_img:
                content.append(Image(chart_img, width=6*inch, height=3.5*inch))
            content.append(Spacer(1, 20))
        
        # d. Списки зачисленных
        content.append(PageBreak())
        content.append(Paragraph("СПИСКИ ЗАЧИСЛЕННЫХ АБИТУРИЕНТОВ", heading_style))
        
        enrolled = report.get('enrolled', {})
        for code, name in program_names.items():
            enrolled_list = enrolled.get(code, [])
            content.append(Paragraph(f"<b>{name}</b> ({len(enrolled_list)} чел.)", heading3_style))
            
            if enrolled_list:
                enrolled_data = [['№', 'ID абитуриента', 'Сумма баллов']]
                for idx, student in enumerate(enrolled_list[:50], 1):  # Ограничим 50 на страницу
                    enrolled_data.append([
                        str(idx),
                        str(student.get('id', 'N/A')),
                        str(student.get('total', 'N/A'))
                    ])
                
                enrolled_table = Table(enrolled_data, colWidths=[0.5*inch, 2*inch, 2*inch])
                enrolled_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5c6bc0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
                    ('FONTNAME', (0, 0), (-1, 0), RUSSIAN_FONT_BOLD),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8eaf6')])
                ]))
                content.append(enrolled_table)
            else:
                content.append(Paragraph("Нет зачисленных", italic_style))
            
            content.append(Spacer(1, 15))
        
        # e. Статистика по каждой ОП
        content.append(PageBreak())
        content.append(Paragraph("СТАТИСТИКА ПО ОБРАЗОВАТЕЛЬНЫМ ПРОГРАММАМ", heading_style))
        
        summary = report.get('summary', {})
        programs = summary.get('programs', {})
        
        if programs:
            stats_data = [
                ['Показатель', 'ПМ', 'ИВТ', 'ИТСС', 'ИБ']
            ]
            
            # Формируем строки таблицы
            rows = [
                ('Общее кол-во заявлений', 'total_applications'),
                ('Количество мест на ОП', 'capacity'),
                ('Кол-во заявлений 1-го приоритета', 'applications_priority_1'),
                ('Кол-во заявлений 2-го приоритета', 'applications_priority_2'),
                ('Кол-во заявлений 3-го приоритета', 'applications_priority_3'),
                ('Кол-во заявлений 4-го приоритета', 'applications_priority_4'),
                ('Кол-во зачисленных 1-го приоритета', 'enrolled_priority_1'),
                ('Кол-во зачисленных 2-го приоритета', 'enrolled_priority_2'),
                ('Кол-во зачисленных 3-го приоритета', 'enrolled_priority_3'),
                ('Кол-во зачисленных 4-го приоритета', 'enrolled_priority_4'),
            ]
            
            for label, key in rows:
                row = [label]
                for code in ['pm', 'ivt', 'itss', 'ib']:
                    value = programs.get(code, {}).get(key, 0)
                    row.append(str(value))
                stats_data.append(row)
            
            stats_table = Table(stats_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
                ('FONTNAME', (0, 0), (-1, 0), RUSSIAN_FONT_BOLD),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e3f2fd')]),
                # Подсветка строки с количеством мест
                ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#c5cae9')),
                ('FONTNAME', (0, 2), (-1, 2), RUSSIAN_FONT_BOLD),
            ]))
            content.append(stats_table)
        
        # Сохраняем PDF
        doc.build(content)
        
        return pdf_path
    
    def _create_dynamics_chart(self):
        """
        Создание графика динамики проходных баллов.
        
        Returns:
            BytesIO: изображение графика или None
        """
        if len(self.reports) < 2:
            return None
        
        # Собираем данные по дням
        dates = []
        data_by_program = {
            'pm': [],
            'ivt': [],
            'itss': [],
            'ib': []
        }
        
        for report in sorted(self.reports, key=lambda r: r['date_folder']):
            dates.append(report['date_folder'])
            passing = report.get('passing_score', {})
            
            for prog in data_by_program.keys():
                score = passing.get(prog)
                data_by_program[prog].append(score)
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_pos = list(range(len(dates)))
        
        # Словарь с настройками для каждой программы
        program_settings = {
            'pm': {'label': 'ПМ', 'color': '#1976d2', 'marker': 'o'},
            'ivt': {'label': 'ИВТ', 'color': '#388e3c', 'marker': 's'},
            'itss': {'label': 'ИТСС', 'color': '#f57c00', 'marker': '^'},
            'ib': {'label': 'ИБ', 'color': '#d32f2f', 'marker': 'D'}
        }
        
        # Рисуем линии для каждой программы
        for prog, scores in data_by_program.items():
            # Фильтруем None значения для отображения
            valid_points = [(i, score) for i, score in enumerate(scores) if score is not None]
            
            if valid_points:
                x_valid = [p[0] for p in valid_points]
                y_valid = [p[1] for p in valid_points]
                
                settings = program_settings[prog]
                ax.plot(
                    x_valid, 
                    y_valid, 
                    marker=settings['marker'], 
                    linewidth=2.5, 
                    markersize=8,
                    label=settings['label'], 
                    color=settings['color'],
                    linestyle='-',
                    alpha=0.8
                )
        
        ax.set_xlabel('День', fontsize=12, fontweight='bold')
        ax.set_ylabel('Проходной балл', fontsize=12, fontweight='bold')
        ax.set_title('Динамика проходных баллов по дням', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(dates, fontsize=10)
        ax.legend(loc='best', fontsize=11, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Добавляем отступы по Y
        if ax.get_ylim()[0] > 0:
            ax.set_ylim(bottom=ax.get_ylim()[0] * 0.95, top=ax.get_ylim()[1] * 1.05)
        
        # Сохраняем в BytesIO
        img_buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer

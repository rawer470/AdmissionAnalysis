# AdmissionAnalysis

Система автоматизированного анализа конкурсных ситуаций при поступлении абитуриентов в вуз с учётом приоритетов заявлений и расчётом вероятности зачисления.

## Описание

AdmissionAnalysis — это программное обеспечение для оптимизации работы приёмных комиссий вузов, позволяющее:

-  Автоматически рассчитывать вероятность поступления на основе конкурсных списков
-  Анализировать данные в динамике по дням приёмной кампании
-  Отслеживать изменение проходных баллов
-  Формировать отчётность и визуализацию результатов
-  Учитывать приоритеты абитуриентов (до 4 программ на человека)

Система использует алгоритм **Deferred Acceptance** (отложенного принятия) для справедливого распределения абитуриентов по образовательным программам.

##  Возможности

### Основной функционал

1. **Управление конкурсными списками**
   - Загрузка данных из CSV/JSON
   - Обновление базы данных абитуриентов
   - Поддержка нескольких дней приёмной кампании

2. **Расчёт зачисления**
   - Алгоритм распределения по приоритетам
   - Учёт согласий на зачисление
   - Автоматическое разрешение конфликтов при равных баллах

3. **Аналитика и отчёты**
   - Проходные баллы на каждую образовательную программу
   - Динамика проходных баллов по дням
   - Списки зачисленных с ID и баллами
   - Детальная статистика по приоритетам
   - Конкурсная ситуация (конкурс на место, недобор)

4. **Статистика по приоритетам**
   - Количество заявлений 1-4 приоритета
   - Количество зачисленных по каждому приоритету
   - Анализ "перетекания" между программами

##  Технологии

### Backend
- **ASP.NET Core MVC** (.NET 10) — веб-приложение, UI
- **Python 3.12** — аналитический движок
- **FastAPI** — Python API-сервис с HTTP API для интеграции (`src/analysis/api_manager.py`)
- **AnalysisService** — C# обёртка для вызова Python API из ASP.NET (`src/web/Services/AnalysisService.cs`)

### Python библиотеки
- `pandas` — обработка данных
- `pdfplumber` — извлечение данных из PDF
- `matplotlib` — визуализация

### Frontend
- Bootstrap 5
- jQuery
- jQuery Validation

##  Структура проекта

```
AdmissionAnalysis/
├── AdmissionAnalysis.sln        # Solution (.NET)
├── makefile                     # Удобные команды запуска (api/web/dev/analyze/pdf)
├── claude.md                    # Архитектура/контекст проекта
├── src/
│   ├── web/                    # ASP.NET Core веб-приложение
│   │   └── WebApp/
│   │       ├── Controllers/    # MVC контроллеры
│   │       ├── Services/       # Сервисы (AnalysisService для вызова Python API)
│   │       ├── Views/          # Razor представления
│   │       └── wwwroot/        # Статические файлы (CSS, JS)
│   │
│   ├── analysis/               # Python аналитический модуль
│   │   ├── admission_stats.py  # Основной класс AdmissionManager
│   │   ├── api_manager.py       # FastAPI сервис (эндпойнты анализа/генерации PDF)
│   │   ├── report_manager.py    # Генерация PDF по stats.json
│   │   ├── requirements.txt    # Python зависимости
│   │   └── testLogic/          # Тесты и демонстрации
│   │       ├── test_admission.py
│   │       ├── test_csv.py
│   │       └── demo_summary.py
│   │
│   └── shared/                 # Общие компоненты (будущее)
│
├── data/                       # Рабочие данные (в .gitignore)
│   ├── uploads/                # Загруженные пользователем файлы
│   ├── extracted/              # Извлечённые таблицы
│   ├── reports/                # Сгенерированные отчёты
│   ├── tmp/                    # Временные файлы
│   └── mock/                   # Тестовые данные
│       ├── 01/                 # Данные за 01.08
│       ├── 02/                 # Данные за 02.08
│       ├── 03/                 # Данные за 03.08
│       └── 04/                 # Данные за 04.08
│
├── docs/                       # Документация
│   ├── STRUCTURE.txt           # Описание структуры
│   └── AdmissionManager_CLASS.txt  # API класса AdmissionManager
│   └── API_MANAGER_API.txt     # Документация по FastAPI сервису (api_manager.py)
│   └── Командный кейс № 3 «Анализ поступления».pdf  # ТЗ проекта
│
├── docker/                     # Docker конфигурация (будущее)
├── env.example                 # Пример переменных окружения
└── README.md                   # Этот файл
```

##  Установка и настройка

### Предварительные требования

- **.NET SDK 10.0+** (для веб-приложения)
- **Python 3.12+** (для аналитики)
- **Git** (для клонирования репозитория)

### Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd AdmissionAnalysis
```

### Шаг 2: Настройка Python окружения

```bash
# Создание виртуального окружения
cd src/analysis
python3 -m venv .venv

# Активация (Linux/macOS)
source .venv/bin/activate

# Активация (Windows)
.venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### Шаг 3: Настройка .NET приложения

```bash
cd src/web/WebApp
dotnet restore
dotnet build
```

**Важно:** Убедитесь, что в `Program.cs` зарегистрирован `AnalysisService`:

```csharp
builder.Services.AddHttpClient<AnalysisService>(client =>
{
    client.BaseAddress = new Uri("http://localhost:8000");
});
```

### Шаг 4: Настройка переменных окружения

```bash
# Скопируйте файл с примером
cp env.example .env

# Отредактируйте .env при необходимости
# DATA_DIR=./data
# PYTHON_SERVICE_URL=http://localhost:8000
```

### Шаг 5: Создание папок для данных

```bash
# Из корня проекта
mkdir -p data/{uploads,extracted,reports,tmp}
```

##  Использование

### Python API (AdmissionManager)

#### Базовый пример

```python
from admission_stats import AdmissionManager

# Загрузка данных
data = {
    'pm': [
        {'id': 101, 'consent': True, 'priority': 1, 'total': 285, ...},
        {'id': 102, 'consent': True, 'priority': 2, 'total': 270, ...},
        # ...
    ],
    'ivt': [...],
    'itss': [...],
    'ib': [...]
}

# Квоты мест
capacity = {
    'pm': 40,   # Прикладная математика
    'ivt': 50,  # Информатика и вычислительная техника
    'itss': 30, # Инфокоммуникационные технологии
    'ib': 20    # Информационная безопасность
}

# Создание менеджера
manager = AdmissionManager(data, capacity)

# Получение проходных баллов
scores = manager.calculate_passing_score()
print(f"Проходной балл на ПМ: {scores['pm']}")

# Получение списков зачисленных
enrolled = manager.generate_enrollment_lists()
print(f"Зачислено на ПМ: {len(enrolled['pm'])} человек")

# Полный отчёт
report = manager.get_statistics_report()
```

### Python API сервис (FastAPI)

В проекте есть FastAPI сервис (`src/analysis/api_manager.py`) с базовыми эндпойнтами:
- `GET /health`
- `GET /api/analyze/{date_folder}`
- `GET /api/generate_pdf_report`
- `GET /api/uploads`
- `GET /api/programs`

Запуск (варианты):

```bash
# вариант 1: напрямую
cd src/analysis
python3 api_manager.py

# вариант 2: через Makefile из корня репозитория
make api
```

Примеры вызовов:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/analyze/03
curl "http://127.0.0.1:8000/api/generate_pdf_report?date_folders=01,02,03,04&target_date=04"
```

Примечание по данным:
- В текущей конфигурации `load_csv_from_uploads()` использует **mock-режим** (`data/mock/<date_folder>`), а строка для `data/uploads/<date_folder>` закомментирована. Подробности см. `docs/API_MANAGER_API.txt`.

### C# интеграция (AnalysisService)

Для удобной работы с Python API из ASP.NET создан сервис `AnalysisService` в `src/web/Services/AnalysisService.cs`.

#### Регистрация в Program.cs

```csharp
// Регистрация HttpClient с AnalysisService
builder.Services.AddHttpClient<AnalysisService>(client =>
{
    client.BaseAddress = new Uri("http://localhost:8000");
});
```

#### Использование в контроллере

```csharp
public class AnalysisController : Controller
{
    private readonly AnalysisService _analysisService;

    public AnalysisController(AnalysisService analysisService)
    {
        _analysisService = analysisService;
    }

    // Проверка здоровья API
    public async Task<IActionResult> Health()
    {
        var result = await _analysisService.GetHealthAsync();
        return Json(result);
    }

    // Анализ одного дня
    public async Task<IActionResult> AnalyzeDay(string day)
    {
        var result = await _analysisService.AnalyzeAsync(day);
        return Json(result);
    }

    // Анализ всех дней сразу (параллельно)
    public async Task<IActionResult> AnalyzeAll()
    {
        var results = await _analysisService.AnalyzeAllDaysAsync();
        return Json(results);
    }

    // Генерация PDF отчёта
    public async Task<IActionResult> GeneratePdf()
    {
        var result = await _analysisService.GeneratePdfReportAsync(
            dateFolders: "01,02,03,04",
            targetDate: "04"
        );
        return Json(result);
    }

    // Список программ
    public async Task<IActionResult> Programs()
    {
        var result = await _analysisService.GetProgramsAsync();
        return Json(result);
    }
}
```

#### Доступные методы AnalysisService

| Метод | Описание |
|-------|----------|
| `GetHealthAsync()` | Проверка здоровья Python API |
| `GetUploadsAsync()` | Список загруженных папок |
| `GetProgramsAsync()` | Список образовательных программ |
| `AnalyzeAsync(dateFolder, ...)` | Анализ данных за один день |
| `AnalyzeAllDaysAsync(...)` | Параллельный анализ всех дней (01-04) |
| `GeneratePdfReportAsync(...)` | Генерация PDF отчёта |

#### Анализ динамики по дням

```python
# Данные за 4 дня приёмной кампании
data_by_days = {
    '01.08': load_data('data/mock/01/'),
    '02.08': load_data('data/mock/02/'),
    '03.08': load_data('data/mock/03/'),
    '04.08': load_data('data/mock/04/')
}

# Расчёт динамики проходных баллов
dynamics = AdmissionManager.calculate_dynamics(data_by_days, capacity)

# Вывод изменений для каждой программы
for prog, dyn in dynamics.items():
    print(f"\n{dyn['program_name']}:")
    for date, score in dyn['by_date'].items():
        print(f"  {date}: {score}")
```

### Запуск веб-приложения

**Важно:** Сначала запустите Python API (см. выше), затем веб-приложение.

```bash
cd src/web/WebApp
dotnet run

# Приложение доступно по адресу:
# https://localhost:5001
# Также в проекте настроен запуск по HTTP на http://localhost:5002 (см. makefile / launchSettings.json)
```

**Для одновременного запуска** обоих сервисов используйте:
```bash
make dev    # Запускает API (8000) и Web (5002) параллельно
```

### Быстрый запуск через makefile (рекомендуется)

```bash
make dev          # API + Web параллельно
make analyze DAY=03
make pdf
```

### Запуск тестов

```bash
# Python тесты
cd src/analysis
python3 testLogic/test_admission.py

# Демонстрация функционала
python3 testLogic/demo_summary.py

# Тесты CSV загрузки
python3 testLogic/test_csv.py
```

##  Формат данных

### Структура CSV для конкурсных списков

```csv
id,consent,priority,physicsIct,russian,math,individual,total
101,true,1,90,85,95,10,280
102,true,2,88,80,92,15,275
...
```

### Структура JSON

```json
[
  {
    "id": 101,
    "consent": true,
    "priority": 1,
    "physicsIct": 90,
    "russian": 85,
    "math": 95,
    "individual": 10,
    "total": 280
  }
]
```

### Поля данных

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int | Уникальный идентификатор абитуриента |
| `consent` | bool | Согласие на зачисление |
| `priority` | int | Приоритет программы (1-4) |
| `physicsIct` | int | Балл по физике/ИКТ |
| `russian` | int | Балл по русскому языку |
| `math` | int | Балл по математике |
| `individual` | int | Балл за индивидуальные достижения |
| `total` | int | Сумма баллов |

##  Образовательные программы

| Код | Название | Мест |
|-----|----------|------|
| `pm` | Прикладная математика | 40 |
| `ivt` | Информатика и вычислительная техника | 50 |
| `itss` | Инфокоммуникационные технологии и системы связи | 30 |
| `ib` | Информационная безопасность | 20 |

##  Тестирование

Проект включает комплексный набор тестов:

### 1. Тесты алгоритма распределения

```bash
python3 src/analysis/testLogic/test_admission.py
```

**Проверяет:**
-  Корректность проходных баллов
-  Правильность списков зачисленных
-  Конкурсную статистику
-  Формирование отчётов
-  Обработку абитуриентов без согласия
-  Детальную статистику по приоритетам

### 2. Демонстрация функционала

```bash
python3 src/analysis/testLogic/demo_summary.py
```

**Показывает:**
- Проходные баллы на ОП
- Динамику по дням
- Списки зачисленных
- Детальную статистику

### 3. Тесты загрузки CSV

```bash
python3 src/analysis/testLogic/test_csv.py
```

**Проверяет:**
- Корректность чтения CSV файлов
- Обработку тестовых данных за 4 дня

## 📚 Документация API

Полная документация класса `AdmissionManager` доступна в файле:

```
docs/AdmissionManager_CLASS.txt
```

Также полезные материалы:
- `claude.md` — архитектурная справка/контекст проекта
- `docs/API_MANAGER_API.txt` — документация по `api_manager.py`
- `docs/Командный кейс № 3 «Анализ поступления».pdf` — ТЗ проекта

### Основные методы

| Метод | Описание |
|-------|----------|
| `__init__(data, capacity)` | Инициализация менеджера |
| `calculate_passing_score()` | Расчёт проходных баллов |
| `generate_enrollment_lists()` | Формирование списков зачисленных |
| `calculate_competition_stats()` | Конкурсная статистика |
| `get_statistics_report()` | Полный отчёт |
| `calculate_dynamics()` | Динамика по дням (статический) |

##  Алгоритм Deferred Acceptance

Система использует алгоритм отложенного принятия для справедливого распределения:

1. **Каждый абитуриент подаётся на программу с приоритетом 1**
2. **Программа оставляет топ по баллам** (в пределах мест)
3. **Отклонённые подают на приоритет 2**, затем 3, затем 4
4. **Процесс повторяется до стабилизации**

### Правила сортировки

1. Сумма баллов (по убыванию)
2. ID абитуриента (по возрастанию при равенстве)

### Особенности

-  Каждый абитуриент зачисляется **максимум в одну** программу
-  Учитываются **только абитуриенты с согласием** (consent=true)
-  Если абитуриент закрепился на высоком приоритете, его баллы **не участвуют** в конкурсе на низкие приоритеты
-  Гарантия завершения за **O(n × 4)** операций

##  Пример вывода отчёта

```
1. ПРОХОДНЫЕ БАЛЛЫ НА ОБРАЗОВАТЕЛЬНЫЕ ПРОГРАММЫ
----------------------------------------------------------------------
  Прикладная математика                                          285
  Информатика и вычислительная техника                            270
  Инфокоммуникационные технологии и системы связи                 265
  Информационная безопасность                                     290

2. ДИНАМИКА ПРОХОДНОГО БАЛЛА ПО ДНЯМ
----------------------------------------------------------------------
  Прикладная математика:
    01.08:  НЕДОБОР
    02.08:  275
    03.08:  280
    04.08:  285

4. ДЕТАЛЬНАЯ СТАТИСТИКА ПО КАЖДОЙ ОБРАЗОВАТЕЛЬНОЙ ПРОГРАММЕ
----------------------------------------------------------------------
  Прикладная математика
    Общее кол-во заявлений:           95
    Количество мест на ОП:            40
    Кол-во заявлений 1-го приоритета: 45
    Кол-во заявлений 2-го приоритета: 30
    Кол-во заявлений 3-го приоритета: 15
    Кол-во заявлений 4-го приоритета: 5
    Кол-во зачисленных 1-го приоритета: 35
    Кол-во зачисленных 2-го приоритета: 3
    Кол-во зачисленных 3-го приоритета: 2
    Кол-во зачисленных 4-го приоритета: 0
```

##  Вклад в проект

Приветствуются любые улучшения:

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменений (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

##  Лицензия

Проект разработан в рамках Московской предпрофессиональной олимпиады школьников (профиль «Информационные технологии»).

##  Авторы
- Lev Shapovalov
- Mark Shapovalov
- Artem Kolerov
- Разработка: Декабрь 2025
- Проект: Командный кейс №3 «Анализ поступления»

##  Контакты

Для вопросов и предложений создавайте Issue в репозитории проекта.
rawer470@gmail.com
---

**Версия:** 1.1
**Последнее обновление:** Январь 2026


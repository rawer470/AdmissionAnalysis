# API Manager - Инструкция по использованию

## Концепция

API работает с файлами из папки `data/uploads/`. Вместо POST запросов с данными, вы:
1. Загружаете CSV файлы в `data/uploads/{дата}/`
2. Вызываете GET endpoint для анализа
3. Получаете результаты в ответе

## Структура папок

```
data/
└── uploads/          # Загруженные CSV файлы
    ├── 01-08/       # Папка с данными за 01.08
    │   ├── PM.csv
    │   ├── IVT.csv
    │   ├── ITSS.csv
    │   └── IB.csv
    └── 02-08/       # Папка с данными за 02.08
        └── ...
```

## Endpoints

### `GET /health`
Проверка работоспособности сервиса.

**Пример:**
```bash
curl http://localhost:8000/health
```

### `GET /api/uploads`
Получить список папок в uploads/.

**Ответ:**
```json
{
  "success": true,
  "folders": ["01-08", "02-08", "03-08"],
  "count": 3
}
```

### `GET /api/analyze/{date_folder}`
Анализировать данные из указанной папки.

**Параметры:**
- `date_folder` (обязательный) — имя папки в uploads/
- `capacity_pm` (опционально) — места на ПМ, по умолчанию 40
- `capacity_ivt` (опционально) — места на ИВТ, по умолчанию 50
- `capacity_itss` (опционально) — места на ИТСС, по умолчанию 30
- `capacity_ib` (опционально) — места на ИБ, по умолчанию 20

**Пример:**
```bash
# С квотами по умолчанию
curl http://localhost:8000/api/analyze/01-08

# С кастомными квотами
curl "http://localhost:8000/api/analyze/01-08?capacity_pm=35&capacity_ivt=45"
```

**Ответ:**
```json
{
  "success": true,
  "date_folder": "01-08",
  "files_processed": ["pm", "ivt", "itss", "ib"],
  "data": {
    "passing_score": {...},
    "enrolled": {...},
    "summary": {...}
  }
}
```

### `GET /api/programs`
Список образовательных программ.

## Формат CSV файлов

Каждый CSV должен содержать:
```csv
id,consent,priority,physicsIct,russian,math,individual,total
101,true,1,90,85,95,10,280
102,true,2,88,80,92,15,275
```

## Workflow использования

### 1. Подготовка данных

```bash
# Создайте папку для даты
mkdir -p data/uploads/01-08

# Скопируйте CSV файлы
cp path/to/PM.csv data/uploads/01-08/
cp path/to/IVT.csv data/uploads/01-08/
cp path/to/ITSS.csv data/uploads/01-08/
cp path/to/IB.csv data/uploads/01-08/
```

### 2. Запуск сервера

```bash
cd src/analysis
python3 api_manager.py
```

### 3. Анализ данных

```bash
# Через curl
curl http://localhost:8000/api/analyze/01-08

# Через браузер
# http://localhost:8000/docs (Swagger UI)
```

### 4. Результаты

Результаты возвращаются в JSON ответе

## Тестирование

```bash
# 1. Подготовьте тестовые данные
cp -r data/mock/01 data/uploads/

# 2. Запустите сервер
python3 api_manager.py

# 3. В другом терминале запустите тесты
python3 testLogic/test_api.py
```

## Интеграция с ASP.NET

```csharp
using System.Net.Http;
using System.Text.Json;

var client = new HttpClient();

// Анализ данных
var response = await client.GetAsync(
    "http://localhost:8000/api/analyze/01-08"
);

var json = await response.Content.ReadAsStringAsync();
var result = JsonSerializer.Deserialize<ApiResponse>(json);

// Использование результатов
var passingScores = result.Data.PassingScore;
```

## Документация

После запуска сервера:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


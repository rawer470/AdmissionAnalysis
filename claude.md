# AdmissionAnalysis - Architecture Reference for AI Agent

## Project Context

This project implements "Case 3: Admission Analysis" from the Moscow Pre-Professional Olympiad for Schoolchildren (IT Profile). The system automates analysis of university admission competition data.

**Source**: Командный кейс № 3 «Анализ поступления» - Московская предпрофессиональная олимпиада школьников, профиль «Информационные технологии»

---

## Technical Requirements from Specification

### Core Functional Requirements

1. **Database**: Store applicant information, scores, priorities, and competition lists. No specific DB technology required.

2. **Data Import**: Load competition lists from external tabular sources (CSV).

3. **Data Update Logic**:
   - If DB is empty: full import from competition lists
   - DELETE: Remove applicant if absent in new list but present in DB
   - ADD: Add applicant if present in new list but absent in DB
   - UPDATE: Update applicant data if present in both (new list takes priority)
   - **Performance**: Loading must complete within 5 seconds

4. **Test Data**: Use 4 lists per program corresponding to 4 days (01.08, 02.08, 03.08, 04.08)

### Educational Programs and Capacity

| Code | Russian Name | English Name | Capacity |
|------|--------------|--------------|----------|
| pm | Прикладная математика (ПМ) | Applied Mathematics | 40 |
| ivt | Информатика и вычислительная техника (ИВТ) | Computer Science | 50 |
| itss | Инфокоммуникационные технологии и системы связи (ИТСС) | ICT Systems | 30 |
| ib | Информационная безопасность (ИБ) | Information Security | 20 |

### Competition List Structure

Each applicant record must contain:

| Field | Type | Description |
|-------|------|-------------|
| id | int | Unique applicant identifier |
| consent | boolean | Consent to enrollment |
| priority | int | Program priority (1-4) |
| physicsIct | int | Physics/ICT score |
| russian | int | Russian language score |
| math | int | Mathematics score |
| individual | int | Individual achievements score |
| total | int | Total score sum |

### Applicant Counts by Date and Program

| Date | PM | IVT | ITSS | IB |
|------|-----|------|------|-----|
| 01.08 | 60 | 100 | 50 | 70 |
| 02.08 | 380 | 370 | 350 | 260 |
| 03.08 | 1000 | 1150 | 1050 | 800 |
| 04.08 | 1240 | 1390 | 1240 | 1190 |

### Applicant Overlap Requirements

One applicant can participate in 1-4 programs. The data must include overlaps:
- Applicants in exactly 1 program
- Applicants in exactly 2 programs
- Applicants in exactly 3 programs
- Applicants in all 4 programs

### Required Demonstration Scenarios

**Test 1 (01.08)**: All programs must show "NEDOBOR" (shortage) - fewer applicants with consent than available seats.

**Test 2 (02.08)**: Calculate passing score for each program. Passing score must be calculable (enough applicants with consent).

**Test 3 (03.08)**: 
- PM and IVT: passing score must INCREASE relative to 02.08
- ITSS and IB: passing score must DECREASE relative to 02.08

**Test 4 (04.08)**:
- All programs: passing score must INCREASE relative to 03.08
- Final ranking by passing score (highest to lowest): PM > IB > IVT > ITSS

### PDF Report Requirements (Section 2.14)

Report must include:
- a) Date and time of report generation
- b) Passing score per program (or "NEDOBOR" status)
- c) Passing score dynamics charts
- d) Enrolled applicants lists (ID + total score)
- e) Statistics per program:
  - Total applications count
  - Seats available
  - Applications by priority (1, 2, 3, 4)
  - Enrolled by priority (1, 2, 3, 4)

---

## Technology Stack

### Python Backend (src/analysis/)
- **Runtime**: Python 3.x
- **Framework**: FastAPI with uvicorn
- **PDF Generation**: reportlab
- **Charts**: matplotlib
- **Data Processing**: csv (standard library), pandas (available)

### Web Frontend (src/web/WebApp/)
- **Runtime**: .NET 9/10
- **Framework**: ASP.NET Core MVC
- **UI Libraries**: Bootstrap, jQuery

### Integration
- Python service: `http://localhost:8000`
- ASP.NET calls Python API via HTTP (CORS enabled)
- Communication format: JSON

---

## Directory Structure

```
/
├── src/
│   ├── analysis/                  # Python service
│   │   ├── admission_stats.py     # AdmissionManager class - core logic
│   │   ├── api_manager.py         # FastAPI endpoints
│   │   ├── report_manager.py      # ReportManager class - PDF generation
│   │   ├── requirements.txt       # Python dependencies
│   │   └── testLogic/             # Test files
│   │
│   └── web/WebApp/                # ASP.NET MVC application
│       ├── Controllers/
│       ├── Views/
│       ├── Program.cs
│       └── WebApp.csproj
│
├── data/                          # Data directory (gitignored)
│   ├── uploads/                   # User-uploaded CSV files
│   │   └── {date_folder}/         # e.g., "01", "02", "03", "04"
│   ├── mock/                      # Test data (same structure)
│   │   └── {01,02,03,04}/
│   ├── reports/                   # Generated reports
│   │   ├── {date_folder}/
│   │   │   └── stats.json
│   │   └── report_*.pdf
│   ├── extracted/
│   └── tmp/
│
├── docs/                          # Documentation
├── claude.md                      # This file
└── env.example
```

---

## Core Classes

### AdmissionManager (admission_stats.py)

Primary class implementing Deferred Acceptance algorithm for fair applicant distribution.

**Constructor**:
```python
AdmissionManager(applicants_data: dict, program_capacity: dict)
```

**Parameters**:
- `applicants_data`: `{program_code: [applicant_dicts]}`
- `program_capacity`: `{program_code: int}`

**Applicant dict structure**:
```python
{
    'id': int,           # Unique applicant ID
    'consent': bool,     # Consent to enrollment (only True participates)
    'priority': int,     # Priority 1-4 for this program
    'total': int,        # Total score
    'math': int,         # Math score
    'russian': int,      # Russian language score
    'physicsIct': int,   # Physics/ICT score
    'individual': int    # Individual achievements score
}
```

**Public Methods**:
- `calculate_competition_stats()` - Competition statistics per program
- `calculate_passing_score()` - Passing scores (None = shortage/NEDOBOR)
- `generate_enrollment_lists()` - Enrolled applicants lists
- `get_statistics_report(date_folder, save_to_reports)` - Full report, saves stats.json

**Static Method**:
- `calculate_dynamics(data_by_days, capacity)` - Score dynamics across days

**Algorithm Rules (Deferred Acceptance)**:
1. Only applicants with `consent=True` participate in distribution
2. Each applicant applies to programs in priority order (1 first, then 2, 3, 4)
3. Each program keeps top applicants by score within its capacity
4. Rejected applicants try their next priority
5. Sorting: total score (descending), ID (ascending) for tie-breaking
6. Each applicant enrolled to exactly ONE program maximum
7. Applicant enrolled on higher priority does NOT compete for lower priorities

**Passing Score Calculation**:
- If enrolled count < capacity: return None (NEDOBOR)
- If enrolled count >= capacity: return score of last enrolled applicant

---

### ReportManager (report_manager.py)

Manages report loading and PDF generation.

**Key Methods**:
- `add_report(date_folder)` - Load stats.json from reports/{date_folder}/
- `get_reports()` - Get all loaded reports
- `generate_pdf(date_folder, filename)` - Generate PDF report

**PDF Content** (per specification 2.14):
- Report timestamp
- Passing scores table
- Dynamics chart (if multiple dates)
- Enrolled applicants lists (ID + total)
- Statistics per program (applications/enrolled by priority)

---

## API Endpoints (api_manager.py)

Base URL: `http://localhost:8000`

### GET /
Returns service info.

### GET /health
Returns `{"status": "healthy"}`.

### GET /api/analyze/{date_folder}
Analyze CSV files and calculate statistics.

**Path Parameters**:
- `date_folder`: Folder name ("01", "02", "03", "04")

**Query Parameters** (optional):
- `capacity_pm`: int (default 40)
- `capacity_ivt`: int (default 50)
- `capacity_itss`: int (default 30)
- `capacity_ib`: int (default 20)

**Behavior**:
1. Loads CSV from data/mock/{date_folder}/ (currently hardcoded)
2. Runs AdmissionManager analysis
3. Saves stats.json to data/reports/{date_folder}/
4. Returns JSON report

### GET /api/generate_pdf_report
Generate PDF from saved stats.json files.

**Query Parameters** (optional):
- `date_folders`: Comma-separated ("01,02,03,04")
- `target_date`: Target date for main data

### GET /api/uploads
List folders in data/uploads/.

### GET /api/programs
Returns program codes and names.

---

## CSV File Format

**Filename Pattern**: `{date}_{PROGRAM_CODE}.csv`
- Examples: `01-08_PM.csv`, `02-08_IVT.csv`

**Columns**:
```csv
id,consent,priority,physics_ict,russian,math,individual,total
178,0,1,100,100,100,9,309
85,1,1,95,98,99,10,302
```

**Consent Parsing**:
- True: "1", "true", "True", "TRUE"
- False: everything else (including "0", "false")

**Field Variants**:
- `physics_ict` or `physicsIct` both accepted

---

## Report Statistics Structure

### summary.programs[code]
```python
{
    'program_name': str,              # Full program name
    'passing_score': int | 'NEDOBOR', # Passing score or shortage
    'capacity': int,                  # Available seats
    'total_applications': int,        # Total applications with consent
    'applications_priority_1': int,   # Apps with priority 1
    'applications_priority_2': int,   # Apps with priority 2
    'applications_priority_3': int,   # Apps with priority 3
    'applications_priority_4': int,   # Apps with priority 4
    'enrolled_priority_1': int,       # Enrolled with priority 1
    'enrolled_priority_2': int,       # Enrolled with priority 2
    'enrolled_priority_3': int,       # Enrolled with priority 3
    'enrolled_priority_4': int,       # Enrolled with priority 4
    'total_enrolled': int,            # Total enrolled
    'enrolled_list': [applicant_dicts]
}
```

### summary.overall
```python
{
    'total_capacity': int,                    # Total seats (140)
    'total_enrolled': int,                    # Total enrolled
    'total_applicants_with_consent': int,     # Unique applicants with consent
    'programs_with_shortage': [program_codes] # Programs with NEDOBOR
}
```

---

## Running the Project

### Python Service
```bash
cd src/analysis
pip install -r requirements.txt
python api_manager.py
# Runs on http://localhost:8000
# Swagger: http://localhost:8000/docs
```

### ASP.NET Application
```bash
cd src/web/WebApp
dotnet run
```

---

## Key Constraints

1. **Performance**: Data loading must complete within 5 seconds
2. **Priorities**: Values 1-4 only, strictly ordered
3. **Unique IDs**: Applicant IDs must be unique
4. **Consent**: Only applicants with consent=True are distributed
5. **Data Source**: Currently uses data/mock/ - change to data/uploads/ for production
6. **Font**: PDF requires Arial Unicode for Cyrillic text

---

## Modification Guidelines

### Adding New Endpoint
1. Add function in `api_manager.py` with `@app.get()` or `@app.post()`
2. Use HTTPException with 400/404/500 for errors
3. Return dict with `success` field

### Modifying Analysis Logic
1. Edit `AdmissionManager` class in `admission_stats.py`
2. Preserve method signatures
3. Run tests after changes

### Modifying PDF Output
1. Edit `ReportManager` class in `report_manager.py`
2. Use `RUSSIAN_FONT` constant
3. Test with single and multiple dates

### Switching Mock to Production
In `api_manager.py`, function `load_csv_from_uploads()`:
```python
# Change:
upload_path = MOCK_DIR / date_folder
# To:
upload_path = UPLOADS_DIR / date_folder
```

---

## Testing

Test files in `src/analysis/testLogic/`:
- `test_admission.py` - AdmissionManager tests
- `test_api.py` - API endpoint tests
- `test_csv.py` - CSV parsing tests
- `test_pdf_generator.py` - PDF generation tests

Run:
```bash
cd src/analysis
python testLogic/test_admission.py
```

---

## Common Issues

1. **"Folder not found"**: Check mock vs uploads path in api_manager.py
2. **"No CSV files"**: Files must match `*{PM,IVT,ITSS,IB}*.csv`
3. **Cyrillic in PDF**: Need Arial Unicode font
4. **stats.json missing**: Run /api/analyze/{date} first
5. **NEDOBOR when expecting score**: Not enough applicants with consent=True

---

## Expected Behavior Validation

For demonstration per specification:

| Date | Expected Behavior |
|------|-------------------|
| 01 | All programs: NEDOBOR (shortage) |
| 02 | All programs: passing score calculable |
| 03 | PM, IVT: score UP; ITSS, IB: score DOWN |
| 04 | All: score UP; Ranking: PM > IB > IVT > ITSS |

This behavior depends on test data in data/mock/ being correctly generated.

# Control Contabilidade - Flask Client Management System

## Architecture Overview

This is a Flask-based client management system for Control Contabilidade, featuring a **multi-storage architecture** with Google Sheets as primary backend and local JSON fallback. The system uses a **service-oriented pattern** with dependency injection and graceful degradation.

### Core Components

- **app.py**: Main Flask application with storage service injection and authentication decorators
- **services/**: Service layer implementing storage abstraction pattern
  - `google_sheets_service_account.py`: Primary Google Sheets backend (Service Account auth)
  - `local_storage_service.py`: Fallback JSON storage for development/offline
  - Import services with `check_dependencies.py` fallback pattern for pandas
- **templates/**: Dual template system (`*_modern.html` vs legacy templates)

## Critical Patterns

### Storage Service Abstraction
All storage services implement the same interface: `get_clients()`, `save_client()`, `get_client(id)`, `delete_client(id)`. The app initializes with this priority:
1. Google Sheets Service Account → 2. Google Sheets OAuth → 3. Local JSON storage

```python
# In app.py - service initialization with fallback chain
if USE_SERVICE_ACCOUNT:
    storage_service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
else:
    storage_service = LocalStorageService()  # fallback
```

### Dependency-Optional Import Pattern
Critical for deployment: `check_dependencies.py` dynamically loads services based on available packages:
- `ImportService` (full) requires pandas
- `ImportServiceLite` (fallback) uses only openpyxl
- Services gracefully degrade functionality when dependencies missing

### Authentication & Session Management
Uses Flask sessions with role-based access (`@login_required`, `@admin_required`). User profiles stored in separate Google Sheets tab with bcrypt password hashing via `UserService`.

## Development Workflows

### Local Development Setup
```bash
# Use minimal requirements for fast setup
pip install -r requirements.minimal.txt
# Place service-account-key.json in root for Google Sheets access
python app.py  # Runs on localhost:5000 with debug=True
```

### Production Deployment (Render)
- Uses `requirements.txt` (without pandas for fast builds ~2-3min vs 15-20min)
- Environment variables: `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEETS_ID`
- Entry point: `wsgi.py` with Gunicorn

### Testing Routes
- `/test` - Simple health check endpoint
- `/debug-sistema-real` - Production debugging interface

## Key Conventions

### Client Data Model
50+ fields stored as flat dictionary with specific naming (camelCase frontend, snake_case in some services). Critical fields:
- `nomeEmpresa` (required), `cnpj`, `razaoSocialReceita`
- Boolean flags: `ct`, `fs`, `dp` for department services
- `ativo` status for soft deletion

### Template Inheritance
- `base.html` for full layout, `base_simple.html` for minimal
- Modern templates (`*_modern.html`) use Bootstrap cards and enhanced UX
- Flash message categories: `success`, `error`, `warning`, `info`

### Error Handling Pattern
Extensive debug logging with emoji prefixes (`🔍`, `✅`, `❌`). All service methods return boolean success or dict with `{'success': bool, 'message': str}`.

## Integration Points

### Google Sheets Schema
- Main sheet: 'Clientes!A:BC' (50+ columns)
- User management: 'Usuarios' tab
- Reports management: 'Relatorios' tab
- Meeting minutes: 'Atas' tab (if MeetingService available)

### File Upload System
Excel import via `werkzeug.secure_filename`, stored in `/uploads` temporarily. Template download generates dynamic Excel with proper headers using `openpyxl`.

### Service Account Authentication
Production uses JSON credentials from environment variable `GOOGLE_SERVICE_ACCOUNT_JSON`. Development falls back to `service-account-key.json` file in root.

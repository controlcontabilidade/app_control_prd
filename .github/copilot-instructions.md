# Control Contabilidade - AI Coding Agent Instructions

## Architecture & Service Boundaries
- Flask app with multi-storage backend: Google Sheets (Service Account/OAuth) and local JSON fallback.
- All storage services implement: `get_clients()`, `save_client()`, `get_client(id)`, `delete_client(id)`.
- Service initialization priority: Service Account → OAuth → Local JSON.
- Service layer in `services/` (see `google_sheets_service_account.py`, `local_storage_service.py`).
- Dependency-optional import pattern: `check_dependencies.py` loads full/lite import service based on pandas/openpyxl availability.
- Authentication/session: Flask sessions, role-based decorators (`@login_required`, `@admin_required`), user profiles in Google Sheets tab, bcrypt password hashing.

## Developer Workflows
- Local: `pip install -r requirements.minimal.txt`; run with `python app.py` (debug mode).
- Production (Render):
  - Use `requirements.txt` (no pandas for fast build).
  - Set env vars: `GOOGLE_SERVICE_ACCOUNT_JSON` (single-line, double-quoted JSON), `GOOGLE_SHEETS_ID`.
  - Entry: `wsgi.py` with Gunicorn.
- Testing routes: `/test` (health check), `/debug-sistema-real` (debug interface).

## Data & Template Conventions
- Client model: 50+ fields, flat dict, camelCase for frontend, snake_case in some services.
  - Required: `nomeEmpresa`, `cnpj`, `razaoSocialReceita`.
  - Boolean flags: `ct`, `fs`, `dp`.
  - Soft delete: `ativo`.
- Template inheritance: `base.html` (full), `base_simple.html` (minimal), modern templates (`*_modern.html`) use Bootstrap cards.
- Flash message categories: `success`, `error`, `warning`, `info`.

## Error Handling & Logging
- Debug logging uses emoji prefixes (`🔍`, `✅`, `❌`).
- Service methods return boolean or dict: `{'success': bool, 'message': str}`.

## Integration Points
- Google Sheets schema:
  - Main: 'Clientes!A:BC' (50+ columns)
  - Users: 'Usuarios' tab
  - Reports: 'Relatorios' tab
  - Meetings: 'Atas' tab (if MeetingService enabled)
- File upload: Excel import via `werkzeug.secure_filename`, stored in `/uploads`, template generated with `openpyxl`.
- Service Account: Production uses env var `GOOGLE_SERVICE_ACCOUNT_JSON` (must be valid JSON, single line, double quotes only).

## Key Files & Examples
- `app.py`: Main Flask app, service injection, decorators, route patterns.
- `services/`: Storage, import, user, report, meeting services.
- `check_dependencies.py`: Dependency-based service loader.
- `templates/`: Modern and legacy HTML templates.

---
For new features, follow service abstraction and dependency-optional patterns. Use debug logging and flash categories as shown. See `app.py` and `services/` for concrete examples.

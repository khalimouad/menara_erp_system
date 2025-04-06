# Menara ERP System

A modular ERP system built with FastAPI, SQLAlchemy, and HTMX.

## Framework Stack

- **Language**: Python
- **Web Framework**: FastAPI
- **Database**: SQLAlchemy + Alembic
- **Frontend**: Server-rendered HTML with Jinja2 + Tailwind CSS + HTMX
- **Deployment**: Docker-based

## Core Architecture

### Modular Design
- Core modules system with manifest-based configuration
- Each module is self-contained with models, views, and controllers
- Plugin-based architecture for extensibility

### Database Support
- SQLite for small to mid-range deployments
- PostgreSQL for larger deployments

## Directory Structure

```
Menara Framework/
├── core_modules/       # Core system modules
├── database/           # Database files
├── filestore/          # File storage
├── modules/            # Custom modules
├── extra_modules/      # Additional modules
├── static/             # Static assets
└── templates/          # HTML templates
```

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python main.py
   ```

## License

[MIT License](LICENSE)